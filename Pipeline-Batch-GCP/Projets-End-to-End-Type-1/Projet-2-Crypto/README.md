# Projet 2 : Pipeline Batch Cryptomonnaies End-to-End sur GCP

Ce projet implémente un pipeline de données batch horaire hautement sécurisé extrayant les cours de marché des principales cryptomonnaies (Bitcoin, Ethereum, etc.), les déposant sous format NDJSON dans un Data Lake Cloud Storage, et orchestrant leur ingestion idempotente dans BigQuery pour analyse financière.

---

## 1. Architecture du Répertoire

Le projet respecte rigoureusement la norme industrielle en 5 modules :

```text
Projet-2-Crypto/
├── 01_ingestion/       # [Python] Extraction, validation et NDJSON
│   ├── .env.exemple
│   ├── requirements.txt
│   ├── src/pipeline.py
│   └── tests/test_pipeline.py
├── 02_data_lake/       # [Storage & BigQuery External] Zone brute
│   ├── table_externe.sh         # Script Bash d'automatisation
│   └── sql/01_table_externe.sql # Pur DDL des tables externes
├── 03_serverless/      # [Cloud Functions & Scheduler] Automatisation
│   ├── main.py
│   ├── pipeline.py
│   ├── requirements.txt
│   ├── deployer.sh              # Script Bash de déploiement
│   └── planificateur.sh         # Script Bash d'ordonnancement
├── 04_entrepot/        # [BigQuery Native] Zone conforme dédoublonnée
│   └── sql/
│       ├── 01_table_native.sql  # DDL table partitionnée & clusterisée
│       ├── 02_merge.sql         # MERGE INTO idempotent défensif
│       └── 03_audit.sql         # Contrôles de qualité automatisés
└── 05_restitution/     # [Looker Studio] Couche Métier Gold
    └── sql/
        └── 01_vue_analytique.sql # Vue analytique pour la BI
```

---

## 2. Règles Métier & Garanties d'Intégrité

1. **Secret Manager & Sécurité** : Les clés d'API financières sont sécurisées dans GCP Secret Manager et chargées à la volée en mémoire, sans stockage en clair.
2. **Filtres de validation financière** :
   - `R01 actif financier absent` : Absence de symbole de devise.
   - `R02 cours de valorisation absent` : Absence de prix retourné.
   - `R03 cours negatif ou nul` : Tout cours `<= 0.0` est systématiquement rejeté.
3. **Partitionnement & Clustering** :
   - Table partitionnée sur `DATE(mesure_le)` pour borner les coûts d'interrogation.
   - Clusterisée par `actif` pour des requêtes instantanées par symbole financier.
4. **Bilan Arithmétique Strict** : Validation systématique de `lues == gardees + rejetees`.

---

## 3. Guide Opérationnel Pas à Pas

### Prérequis
Définir le projet GCP courant :
```bash
gcloud config set project deft-smile-511110-q3
```

---

### Module 01 : Ingestion & Validation Locale

1. **Initialisation de l'environnement Python** :
```bash
cd 01_ingestion
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Exécution des tests unitaires** :
```bash
pytest -v tests/
```
*4 tests unitaires valident le format des données, le rejet des prix négatifs, la détection des symboles manquants et la transformation.*

3. **Exécution locale** :
```bash
python3 src/pipeline.py
```

---

### Module 02 : Data Lake & Tables Externes BigQuery

Ce module crée le bucket `data-lake-crypto-${PROJET_ID}`, le dataset `entrepot_crypto`, et applique le DDL des tables externes `raw_crypto` et `raw_crypto_rejets`.

```bash
cd ..
bash 02_data_lake/table_externe.sh
```

**Vérification de la table externe** :
```bash
bq query --use_legacy_sql=false 'SELECT * FROM `entrepot_crypto.raw_crypto` LIMIT 5;'
```

---

### Module 03 : Déploiement Serverless & Ordonnancement

1. **Déploiement de la Cloud Function Gen 2** :
Le script provisionne le compte de service `sa-executeur-crypto`, lui confère les droits Cloud Storage, et déploie le conteneur serverless :
```bash
bash 03_serverless/deployer.sh
```

2. **Planification horaire Cloud Scheduler** :
Configure le déclenchement toutes les heures (`0 * * * *`) via jeton OIDC sécurisé :
```bash
bash 03_serverless/planificateur.sh
```

3. **Déclenchement immédiat pour test** :
```bash
gcloud scheduler jobs run job-ingestion-crypto-horaire --location=europe-west9
```

---

### Module 04 : Entrepôt BigQuery & Fusion Idempotente

1. **Création de la table native** (`clean_cotations`) :
```bash
bq query --use_legacy_sql=false < 04_entrepot/sql/01_table_native.sql
```

2. **Exécution du MERGE défensif** :
```bash
bq query --use_legacy_sql=false < 04_entrepot/sql/02_merge.sql
```

3. **Contrôles de qualité automatisés** :
```bash
bq query --use_legacy_sql=false < 04_entrepot/sql/03_audit.sql
```

---

### Module 05 : Restitution Analytique & Dashboard

Déploiement de la vue Gold calculant la variation de cours, la volatilité et la moyenne mobile :
```bash
bq query --use_legacy_sql=false < 05_restitution/sql/01_vue_analytique.sql
```

Visualisez les indicateurs financiers calculés :
```bash
bq query --use_legacy_sql=false 'SELECT * FROM `entrepot_crypto.vue_cotations_marche` LIMIT 10;'
```
