# Pipeline Batch GCP — Analyse de la mobilité Vélib' Paris

> Projet en construction dans le cadre de ma préparation à l'alternance Data Engineer (formation Liora, intake novembre 2026).
> **Livraison prévue** : octobre 2026.

## Objectif

Construire un pipeline batch complet sur Google Cloud Platform qui ingère les données ouvertes du service Vélib' Métropole, les transforme et produit un tableau de bord d'analyse de la mobilité en Île-de-France.

Le projet vise à démontrer la maîtrise d'un pipeline batch de bout en bout : ingestion API, stockage brut, transformation, modélisation analytique, orchestration, exposition.

## Source de données

- **API Vélib' Métropole** (Open Data) : disponibilité en temps réel des stations
- **API STIF/IDFM** : données complémentaires sur les stations et le réseau
- Volume estimé : ~1 400 stations, snapshots horaires sur 90 jours = ~3 M lignes

## Architecture cible


## Stack technique

- **Ingestion** : Cloud Functions (Python 3.11) déclenchées par Cloud Scheduler
- **Stockage brut** : Cloud Storage (partitionnement par date)
- **Data warehouse** : BigQuery (tables partitionnées + clusterisées)
- **Orchestration** : Cloud Composer (Airflow managé)
- **Transformation** : dbt Core
- **Visualisation** : Looker Studio
- **IaC** : Terraform (provisioning des ressources GCP)
- **CI/CD** : GitHub Actions

## Livrables prévus

- [ ] Code d'ingestion API + script de backfill
- [ ] DAG Airflow orchestrant l'ensemble
- [ ] Modèles dbt (staging → intermediate → marts)
- [ ] Tests de qualité des données (dbt tests)
- [ ] Documentation du modèle analytique
- [ ] Dashboard Looker Studio public
- [ ] Guide de reproductibilité (README technique + Terraform)

## Indicateurs analytiques cibles

- Taux d'occupation moyen par station et par heure
- Stations chroniquement vides / pleines (identification des déséquilibres)
- Flux de rééquilibrage estimés
- Cartographie des zones sous-tension

## État d'avancement

| Étape | Statut |
|---|---|
| Cadrage fonctionnel | ✅ Terminé |
| Setup GCP + Terraform | 🔄 En cours |
| Ingestion API | ⏳ Planifié |
| Modélisation dbt | ⏳ Planifié |
| Orchestration Airflow | ⏳ Planifié |
| Dashboard | ⏳ Planifié |

## Contact

FOFANA Lazeny — [LinkedIn](https://www.linkedin.com/in/abdoul-karim-fofana/)
