# Projet 3 : Pipeline Batch Catalogue d'Entités End-to-End sur GCP

Ce projet implémente un pipeline de données batch complet extrayant et normalisant un catalogue d'entités volumineux et multi-pages (API Rick & Morty / Catalogue d'objets), gérant la pagination automatique, l'ingestion brute dans Cloud Storage, la déclaration de tables externes BigQuery, et l'unification dans un entrepôt analytique dédoublonné.

---

## 1. Architecture du Répertoire

Le projet respecte rigoureusement la norme industrielle en 5 modules :

```text
Projet-3-Catalogue/
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

## 2. Principes & Fonctionnalités Clés

1. **Gestion de la pagination REST** : Le script d'ingestion parcourt de manière exhaustive l'ensemble des pages d'API (42 pages, 826 enregistrements) avec gestion des retries réseau et temporisation adaptative.
2. **Aplatissement et typage défensif** : Les structures JSON imbriquées (`origin.name`, `location.name`) sont aplaties sous format tabulaire NDJSON prêt pour BigQuery.
3. **Partitionnement Hive & Partitionnement Natif** :
   - Data Lake : `gs://data-lake-catalogue-${PROJET_ID}/api_catalogue/dt=YYYY-MM-DD/data.jsonl`.
   - Entrepôt : Partitionnement journalier sur `date_ingestion_utc`, clusterisé par `espece` et `statut`.
4. **Validation Arithmétique Non Négociable** : `lues == gardees + rejetees`.

---

## 3. Guide Opérationnel Pas à Pas

### Prérequis
Positionner le projet GCP actif :
```bash
gcloud config set project deft-smile-511110-q3
```

---

### Module 01 : Ingestion & Validation Locale

1. **Initialisation de l'environnement virtuel** :
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
*3 tests unitaires valident le filtrage des identifiants invalides, la conformité de l'extraction et l'aplatissement des structures.*

3. **Exécution locale de la collecte complète** :
```bash
python3 src/pipeline.py
```
*Extrait 826 enregistrements et les dépose sur Cloud Storage.*

---

### Module 02 : Data Lake & Tables Externes BigQuery

Ce module crée le bucket `data-lake-catalogue-${PROJET_ID}`, le dataset `entrepot_catalogue`, et configure les tables externes DDL `raw_catalogue` et `raw_catalogue_rejets` :

```bash
cd ..
bash 02_data_lake/table_externe.sh
```

**Interrogation immédiate des données Cloud Storage via BigQuery** :
```bash
bq query --use_legacy_sql=false 'SELECT identifiant, nom, espece, statut FROM `entrepot_catalogue.raw_catalogue` LIMIT 10;'
```

---

### Module 03 : Déploiement Serverless & Automatisation

1. **Déploiement de la Cloud Function Gen 2** :
Provisionne le compte de service `sa-executeur-catalogue`, accorde les rôles de stockage et déploie le service :
```bash
bash 03_serverless/deployer.sh
```

2. **Planification Cloud Scheduler** :
Ordonnance l'exécution quotidienne à 04:00 (Europe/Paris) avec authentification OIDC :
```bash
bash 03_serverless/planificateur.sh
```

3. **Test d'exécution du job planifié** :
```bash
gcloud scheduler jobs run job-catalogue-quotidien --location=europe-west9
```

---

### Module 04 : Entrepôt BigQuery & MERGE Idempotent

1. **Création de la table native du catalogue** :
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

### Module 05 : Restitution Analytique Gold

Déploiement de la vue analytique calculant la répartition démographique (espèces, statuts, univers d'origine) :
```bash
bq query --use_legacy_sql=false < 05_restitution/sql/01_vue_analytique.sql
```

**Consultation des métriques finales** :
```bash
bq query --use_legacy_sql=false 'SELECT * FROM `entrepot_catalogue.vue_catalogue` ORDER BY total_personnages DESC LIMIT 15;'
```
