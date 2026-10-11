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

### Les 4 Contrôles Non-Négociables de Fiabilité

Tout pipeline déployé respecte impérativement :
1. **Idempotence absolue** : rejouer une exécution à l'infini donne le même état final (chemins GCS déterministes `annee=YYYY/mois=MM/jour=DD/` et instructions `MERGE INTO` dédoublonnantes dans BigQuery).
2. **Typage strict et rejets tracés** : conversion immédiate à la source, aucune donnée invalide ne pénètre l'entrepôt, chaque rejet est motivé dans un bilan d'audit.
3. **Sécurité et étanchéité des secrets** : zéro clé hardcodée, utilisation exclusive de Secret Manager et de variables d'environnement (`.env`).
4. **Testabilité et observabilité** : suite de tests unitaires automatisés sous `pytest` avant tout déploiement, et logs d'exécution structurés.

---

## 2. La Trajectoire : Où je veux aller

Pour couvrir les grands cas d'usage de l'ingénierie de données sur Google Cloud, mon travail est centré sur la réalisation progressive de **cinq pipelines majeurs End-to-End** :

1. **Pipeline 1 — Météo (API REST & Socle Serverless)** : Ingestion horaire, partitionnement Hive, table externe GCS et chargement MERGE idempotent dans BigQuery *(validé & en production)*.
2. **Pipeline 2 — Données Financières (API Authentifiée & Secrets)** : Sécurité renforcée avec Google Secret Manager, gestion des quotas API, repli exponentiel (Exponential Backoff).
3. **Pipeline 3 — Mobilité & Flux Paginés (API Dynamique)** : Pagination par curseur et offset, condition d'arrêt déterministe, découpage en micro-lots GCS.
4. **Pipeline 4 — Entrepôt Évolutif (Historisation SCD2 & Structures Imbriquées)** : Suivi de validité temporelle (Slowly Changing Dimensions Type 2) et modélisation BigQuery avec `STRUCT` et `REPEATED`.
5. **Pipeline 5 — Réconciliation Multi-Sources & Restitution BI** : Croisement de flux hétérogènes, réconciliation de grains spatio-temporels, dimensions conformes et reporting Looker Studio.

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
- **Objectif** : Alternance Data Engineer (Formation Liora en partenariat avec Mines Paris-PSL)
