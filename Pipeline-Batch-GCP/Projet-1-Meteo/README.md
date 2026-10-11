# Projet 1 — Pipeline Batch Météo End-to-End (GCP)

Pipeline de données batch automatisé, résilient et idempotent, extrayant les relevés météorologiques horaires depuis l'API Open-Meteo pour les charger dans Google Cloud Storage et BigQuery.

---

## 1. Architecture Globale

Le pipeline suit le cycle complet de l'ingénierie des données sur Google Cloud Platform :

```text
[API Open-Meteo]
       │
       ▼  (01_ingestion : extraction batch Python, typage strict, validation)
[Cloud Storage (Data Lake GCS)]
       │  Chemin Hive : gs://<bucket>/meteo/annee=YYYY/mois=MM/jour=DD/meteo_YYYY-MM-DD.jsonl
       ▼
[BigQuery : Table Externe]  (02_data_lake : requêtage direct sans coût de stockage supplémentaire)
       │
       ▼  (03_serverless : Cloud Function Gen 2 déclenchée par Cloud Scheduler)
[BigQuery : Table Native Partitionnée]  (04_entrepot : partition DATE, clusterisation code_postal)
       │  Chargement par MERGE SQL idempotent (zéro doublon garanti)
       ▼
[BigQuery : Vues Analytiques]  (05_restitution : agrégations, KPIs et exposition BI)
```

---

## 2. Structure du Projet

```text
Projet-1-Meteo/
├── .gitignore
├── README.md
├── 01_ingestion/               # Ingestion locale & tests unitaires
│   ├── .env.exemple            # Gabarit des variables d'environnement (sans secrets)
│   ├── requirements.txt        # Dépendances Python (requests, google-cloud-storage, etc.)
│   ├── learning/
│   │   └── 00_audit.py         # Script exploratoire et audit du schéma de l'API
│   ├── src/
│   │   └── pipeline.py         # Code d'ingestion principal (idempotent, validé)
│   └── tests/
│       └── test_pipeline.py    # 12 tests unitaires automatisés (pytest)
├── 02_data_lake/               # Définition du Data Lake Cloud Storage
│   ├── sql/
│   │   └── 01_table_externe.sql # Création de la table externe BigQuery sur GCS
│   └── 02_controle_lake.sql    # Requêtes de validation et d'intégrité du lac
├── 03_serverless/              # Industrialisation Serverless (Cloud Functions Gen 2)
│   ├── main.py                 # Point d'entrée HTTP Cloud Function
│   ├── pipeline.py             # Logique d'extraction et d'écriture Cloud
│   ├── requirements.txt        # Dépendances du runtime Cloud Function
│   └── deployer.sh             # Script de déploiement gcloud automatisé
├── 04_entrepot/                # Entrepôt analytique BigQuery (Data Warehouse)
│   └── sql/
│       ├── 01_table_native.sql # DDL de la table native partitionnée
│       └── 02_merge.sql        # Requête MERGE idempotente (dédoublonnage)
└── 05_restitution/             # Modélisation et vues de consommation
    └── 01_vue_restitution.sql  # Vues analytiques pour reporting et BI
```

---

## 3. Les 4 Piliers de Fiabilité Implémentés

1. **Idempotence stricte** :
   - Dépôt GCS découpé selon un chemin logique déterministe (`meteo/annee=YYYY/mois=MM/jour=DD/meteo_YYYY-MM-DD.jsonl`). Relancer le pipeline écrase le lot du jour sans jamais dupliquer de fichier.
   - Chargement BigQuery via `MERGE` SQL sur clé primaire `(station_id, date_heure)`. Rejouer un lot met à jour l'enregistrement existant au lieu d'insérer un doublon.

2. **Typage strict et validation à la source** :
   - Chaque ligne reçue est castée et validée (conversion ISO 8601 en TIMESTAMP UTC, validation des plages de température et d'humidité).
   - Les données invalides ou corrompues sont rejetées avant écriture dans le lac.

3. **Sécurité et isolation des secrets** :
   - Aucun token, clé d'API ou ID de projet n'est hardcodé.
   - Utilisation exclusive des variables d'environnement (`.env` local, Secret Manager / variables Cloud Function en production).
   - Fichiers `.env` et clés JSON strictement exclus par `.gitignore`.

4. **Testabilité et observabilité** :
   - Suite de tests unitaires automatisés via `pytest` couvrant la conversion des dates, la gestion des erreurs réseau, la structure du payload et l'idempotence.
   - Logs structurés à chaque étape du pipeline.

---

## 4. Démarrage Rapide

### Prérequis
- Python 3.10+
- Un compte Google Cloud Platform avec un projet configuré
- SDK `gcloud` installé et authentifié (`gcloud auth application-default login`)

### Installation locale et tests
```bash
cd 01_ingestion

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables
cp .env.exemple .env
# Renseigner PROJECT_ID, BUCKET_NAME, etc. dans .env

# Lancer la suite de tests unitaires
pytest tests/
```

### Déploiement Serverless (Cloud Functions)
```bash
cd ../03_serverless
chmod +x deployer.sh
./deployer.sh
```

---

## 5. Auteur & Contexte

Projet réalisé par **FOFANA Lazeny** dans le cadre de la préparation à l'alternance Data Engineer.
