# Projet 1 : Pipeline Batch Météo End-to-End sur Google Cloud Platform (GCP)

Ce projet implémente un pipeline de données batch complet, robuste et prêt pour la production, extrayant les observations météorologiques multi-villes depuis l'API Open-Meteo, les intégrant dans un Data Lake Cloud Storage, puis dans un entrepôt BigQuery partitionné et dédoublonné, jusqu'à la couche de restitution analytique Gold pour Looker Studio.

---

## 1. Architecture du Répertoire

Le projet respecte rigoureusement la norme industrielle en 5 modules :

```text
Projet-1-Meteo/
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

## 2. Piliers d'Architecture & Principes de Conception

1. **Idempotence stricte** : Chaque lot quotidien est déposé sous un partitionnement Hive déterministe (`dt=YYYY-MM-DD/mesures.jsonl`). Deux exécutions le même jour remplacent le lot sans dupliquer de lignes.
2. **Gestion explicite des rejets** : Aucune ligne non conforme n'est ignorée silencieusement. Les rejets partent dans un compartiment dédié (`rejets/meteo/dt=...`) avec le motif technique précis du rejet et l'enregistrement brut.
3. **Contrôle d'intégrité arithmétique** : Chaque exécution valide l'assertion stricte : `lues == gardees + rejetees`. Une rupture arithmétique lève immédiatement une exception bloquante.
4. **Cloisonnement Serverless & Moindre Privilège** : La Cloud Function tourne avec un compte de service dédié (`sa-pipeline`), et le Cloud Scheduler l'invoque via un jeton OIDC sécurisé (`sa-declencheur-meteo`).

---

## 3. Guide Opérationnel Pas à Pas

### Prérequis
Assurez-vous d'avoir configuré votre projet GCP actif dans votre terminal :
```bash
gcloud config set project deft-smile-511110-q3
```

---

### Module 01 : Ingestion & Validation Locale

1. **Installation de l'environnement virtuel** :
```bash
cd 01_ingestion
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configuration des variables d'environnement** :
```bash
cp .env.exemple .env
# Renseigner PROJET_ID et BUCKET dans le fichier .env
```

3. **Exécution des tests unitaires** :
Les tests valident les seuils thermiques (-80°C à +60°C), l'exhaustivité des motifs de rejets, la conservation du fuseau et l'arithmétique du bilan.
```bash
pytest -v tests/
```

4. **Exécution locale du pipeline** :
```bash
python3 src/pipeline.py
```

---

### Module 02 : Data Lake & Tables Externes BigQuery

Ce module provisionne le bucket de stockage Cloud Storage, le dataset BigQuery `entrepot_meteo`, et déclare les tables externes BigQuery `raw_meteo` et `rejets_meteo` avec partitionnement Hive.

Exécutez le script d'automatisation :
```bash
cd ..
bash 02_data_lake/table_externe.sh
```

**Vérification BigQuery** :
```bash
bq query --use_legacy_sql=false 'SELECT * FROM `entrepot_meteo.raw_meteo` LIMIT 5;'
```

---

### Module 03 : Déploiement Serverless & Ordonnancement

1. **Déploiement de la Cloud Function Gen 2** :
Le script configure le compte de service, attribue les rôles IAM et déploie le conteneur serverless :
```bash
bash 03_serverless/deployer.sh
```

2. **Planification automatique (Cloud Scheduler)** :
Configure le déclenchement quotidien à 06:00 (Europe/Paris) via appel HTTP authentifié OIDC :
```bash
bash 03_serverless/planificateur.sh
```

3. **Test manuel du déclencheur** :
```bash
gcloud scheduler jobs run job-meteo-quotidien --location=europe-west9
```

---

### Module 04 : Entrepôt BigQuery & Normalisation

1. **Création de la table native conforme** (partitionnée par `dt`, clusterisée par `ville`) :
```bash
bq query --use_legacy_sql=false < 04_entrepot/sql/01_table_native.sql
```

2. **Exécution du MERGE incrémental idempotent** :
```bash
bq query --use_legacy_sql=false < 04_entrepot/sql/02_merge.sql
```

3. **Contrôles de qualité automatisés** :
```bash
bq query --use_legacy_sql=false < 04_entrepot/sql/03_audit.sql
```

---

### Module 05 : Restitution Analytique Gold & Looker Studio

Créez la vue métier pré-agrégée intégrant températures moyennes, amplitudes thermiques et moyenne mobile sur 7 jours :
```bash
bq query --use_legacy_sql=false < 05_restitution/sql/01_vue_analytique.sql
```

**Interrogation de la vue finale** :
```bash
bq query --use_legacy_sql=false 'SELECT * FROM `entrepot_meteo.vue_meteo_journaliere` ORDER BY date_releve DESC, ville LIMIT 10;'
```

Connectez ensuite Looker Studio directement sur la vue `entrepot_meteo.vue_meteo_journaliere`.
