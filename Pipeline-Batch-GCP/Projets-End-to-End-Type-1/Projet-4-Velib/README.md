# Projet 4 : Pipeline Batch Mobilité Vélib' End-to-End sur GCP

Ce projet implémente un pipeline de données batch complet et résilient pour la supervision en temps réel de la mobilité partagée (API Vélib' Métropole / OpenData Paris). Il implémente la pagination automatique par offset, le contrôle volumétrique adaptatif, le stockage partitionné sous Cloud Storage, l'ingestion BigQuery dédoublonnée sur clé composite, et une vue analytique Gold prête pour Looker Studio.

---

## 1. Architecture du Répertoire

Le projet respecte rigoureusement la norme industrielle en 5 modules :

```text
Projet-4-Velib/
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

## 2. Principes Clés d'Ingénierie

1. **Pagination par Offset & Plafond Étanche** : Collecte par paquets de 100 enregistrements jusqu'à concurrence du total déclaré avec plafond `LIMITE_PAGES_MAX` interdisant toute boucle infinie.
2. **Contrôle Volumétrique Adaptatif** : Vérification que le volume collecté se situe à +/- 20% du volume nominal attendu (1 400 stations).
3. **Clé Primaire Composite & MERGE Idempotent** : Dédoublonnage strict sur `(station_id, mesure_le)`.
4. **Filigrane d'Ingestion CDC (Watermark)** : Table d'état `entrepot_mobilite.filigrane_etat` évitant le retraitement de relevés déjà intégrés.

---

## 3. Guide Opérationnel Pas à Pas

### Prérequis
Définir le projet GCP courant :
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
*6 tests unitaires valident le filtrage des identifiants manquants, la positivite des compteurs, le typage et le contrôle volumétrique.*

3. **Exécution locale** :
```bash
python3 src/pipeline.py
```

---

### Module 02 : Data Lake & Tables Externes BigQuery

Ce module crée le bucket `data-lake-mobilite-${PROJET_ID}`, le dataset `entrepot_mobilite`, et applique le DDL des tables externes `raw_velib` et `raw_velib_rejets`.

```bash
cd ..
bash 02_data_lake/table_externe.sh
```

**Vérification de la table externe** :
```bash
bq query --use_legacy_sql=false 'SELECT station_id, nom_station, velos_disponibles FROM `entrepot_mobilite.raw_velib` LIMIT 10;'
```

---

### Module 03 : Déploiement Serverless & Ordonnancement

1. **Déploiement de la Cloud Function Gen 2** :
Active automatiquement les APIs, configure le compte de service `sa-executeur-velib` avec les rôles Storage Admin et BigQuery Admin, et déploie le conteneur serverless :
```bash
bash 03_serverless/deployer.sh
```

2. **Planification Cloud Scheduler** :
Configure le déclenchement toutes les 15 minutes (`*/15 * * * *`) via jeton OIDC sécurisé :
```bash
bash 03_serverless/planificateur.sh
```

3. **Déclenchement immédiat pour test** :
```bash
gcloud scheduler jobs run job-velib-quotidien --location=europe-west9
```

---

### Module 04 : Entrepôt BigQuery & Fusion Idempotente

1. **Création de la table native partitionnée** (`stations_velib`) :
```bash
bq query --use_legacy_sql=false < 04_entrepot/sql/01_table_native.sql
```

2. **Exécution du MERGE défensif sur clé composite** :
```bash
bq query --use_legacy_sql=false < 04_entrepot/sql/02_merge.sql
```

3. **Contrôles de qualité automatisés** :
```bash
bq query --use_legacy_sql=false < 04_entrepot/sql/03_audit.sql
```

---

### Module 05 : Restitution Analytique & Dashboard Looker Studio

Déploiement de la vue Gold calculant les taux de disponibilité par commune et alertant sur les stations vides ou saturées :
```bash
bq query --use_legacy_sql=false < 05_restitution/sql/01_vue_analytique.sql
```

**Consultation des indicateurs de mobilité calculés** :
```bash
bq query --use_legacy_sql=false 'SELECT * FROM `entrepot_mobilite.vue_mobilite_temps_reel` ORDER BY total_stations DESC LIMIT 15;'
```
