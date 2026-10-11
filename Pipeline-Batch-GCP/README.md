# Ingénierie de Pipelines Batch sur Google Cloud Platform (GCP)

> **Portfolio d'alternance Data Engineer** — FOFANA Lazeny  
> Cadre méthodologique, architecture de référence et suivi des projets batch en production.

---

## 1. La Démarche d'Ingénierie

L'objectif de cet espace est de construire des **pipelines de données batch fiables, idempotents et industriels** sur Google Cloud Platform, selon les standards professionnels attendus en entreprise.

Chaque projet est conçu de bout en bout selon une séparation stricte des responsabilités en **cinq modules standardisés** :

```text
┌─────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐      ┌────────────────────────┐      ┌───────────────────────┐
│ 01_ingestion    │ ───► │ 02_data_lake            │ ───► │ 03_serverless           │ ───► │ 04_entrepot            │ ───► │ 05_restitution        │
│ Extraction API  │      │ Cloud Storage (GCS)     │      │ Cloud Functions Gen 2   │      │ BigQuery DataWarehouse │      │ Vues Analytiques SQL  │
│ Typage strict   │      │ Partitionnement Hive    │      │ Cloud Scheduler (Cron)  │      │ Table Native partition │      │ KPIs Décisionnels     │
│ 12 tests pytest │      │ Tables Externes BQ      │      │ Déploiement automatisé  │      │ MERGE SQL Idempotent   │      │ Looker Studio / BI    │
└─────────────────┘      └─────────────────────────┘      └─────────────────────────┘      └────────────────────────┘      └───────────────────────┘
```

### Les 4 Contrôles de Fiabilité

Tout pipeline déployé respecte impérativement :
1. **Idempotence absolue** : rejouer une exécution à l'infini donne le même état final (chemins GCS déterministes `annee=YYYY/mois=MM/jour=DD/` et instructions `MERGE INTO` dédoublonnantes dans BigQuery).
2. **Typage strict et rejets tracés** : conversion immédiate à la source, aucune donnée invalide ne pénètre l'entrepôt, chaque rejet est motivé dans un bilan d'audit.
3. **Sécurité et étanchéité des secrets** : zéro clé hardcodée, utilisation exclusive de Secret Manager et de variables d'environnement (`.env`).
4. **Testabilité et observabilité** : suite de tests unitaires automatisés sous `pytest` avant tout déploiement, et logs d'exécution structurés.

---

## 2. La Trajectoire : Où je veux aller

Pour couvrir l'ensemble des standards du Data Engineering moderne sur Google Cloud, mon parcours est centré sur la réalisation progressive de **cinq pipelines majeurs End-to-End** :

1. **Pipeline 1 — Socle Serverless & Ingestion API Native** *(Validé & en production)*
   - **Démarche** : Ingestion batch en Python pur, validation stricte à la source, stockage Cloud Storage en partitionnement Hive, table externe et chargement `MERGE` idempotent sans doublon dans l'entrepôt BigQuery.
   - **Technologies** : Python 3.11, Cloud Storage, Cloud Functions Gen 2, Cloud Scheduler, BigQuery, Pytest.
2. **Pipeline 2 — Ingestion Outillée & Conteneurisation (ELT & Docker)**
   - **Démarche** : Normalisation de la collecte via des connecteurs d'ingestion managés, exécution de tâches d'extraction conteneurisées et sécurisation cryptographique des identifiants.
   - **Technologies** : Docker, Airbyte, Google Secret Manager, Cloud Storage, BigQuery.
3. **Pipeline 3 — Modélisation Analytique & Qualité de Données (dbt Core)**
   - **Démarche** : Transformation modulaire en couches (*Staging → Intermediate → Marts*), historisation de dimensions à évolution lente (SCD Type 2), modélisation de types imbriqués (`STRUCT`/`REPEATED`) et tests automatisés de contrat de données.
   - **Technologies** : dbt Core, BigQuery SQL, Jinja, dbt-test.
4. **Pipeline 4 — Traitement Distribué & Formats Colonnaires (Apache Spark)**
   - **Démarche** : Ingestion et transformation de gros volumes de données en calcul distribué, conversion au format colonnaire Parquet compressé (Snappy), élagage physique de partitions et exécution en mémoire bornée.
   - **Technologies** : Apache Spark (PySpark), Cloud Dataproc Serverless, Cloud Storage, Apache Parquet.
5. **Pipeline 5 — Orchestration Industrielle & Infrastructure as Code (Airflow & Terraform)**
   - **Démarche** : Orchestration centralisée de bout en bout par DAG (dépendances inter-tâches, alertes de panne, gestion de backfill), exposition décisionnelle BI et déploiement 100 % déclaratif et reproductible de l'infrastructure Cloud.
   - **Technologies** : Apache Airflow (Cloud Composer), Terraform (IaC), Looker Studio, GitHub Actions (CI/CD).

---

## 3. Projets Réalisés en Production

*Ce tableau récapitule les projets finalisés, testés et déployés sur GCP. Il grossit à chaque nouveau projet validé.*

| N° | Projet | Source & Format | Stack GCP | Apport Technique Clé / Pattern | Statut |
|:---:|:---|:---|:---|:---|:---:|
| **01** | [**Projet-1-Meteo**](./Projet-1-Meteo) | API Open-Meteo (JSON horaire) | Cloud Storage, Cloud Functions Gen 2, Cloud Scheduler, BigQuery | **Socle End-to-End complet** : Ingestion batch, Hive Partitioning, Table externe GCS, Table native partitionnée DATE, MERGE idempotent dédoublonnant, suite de 12 tests unitaires pytest. | ✅ **En production** |

---

## 4. Profil

- **Auteur** : FOFANA Lazeny
- **LinkedIn** : [linkedin.com/in/abdoul-karim-fofana](https://www.linkedin.com/in/abdoul-karim-fofana/)
- **Objectif** : Alternance Data Engineer (Formation Master Spécialisé Data and Gan AI engineering à EFREI
