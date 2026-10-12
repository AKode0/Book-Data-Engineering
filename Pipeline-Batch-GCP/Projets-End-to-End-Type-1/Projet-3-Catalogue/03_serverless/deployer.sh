#!/usr/bin/env bash
# ==============================================================================
# Déploiement Cloud Functions Gen 2 - Pipeline Catalogue
# ==============================================================================
set -euo pipefail

# Se placer dans le répertoire du script (03_serverless)
cd "$(dirname "$0")"

PROJET_ID=$(gcloud config get-value project)
BUCKET_NAME="data-lake-catalogue-${PROJET_ID}"
REGION="europe-west9"
SA_NAME="sa-executeur-catalogue"
SERVICE_ACCOUNT="${SA_NAME}@${PROJET_ID}.iam.gserviceaccount.com"

echo "=== 1. Vérification et création du compte de service exécuteur ==="
gcloud iam service-accounts create "${SA_NAME}"   --display-name="Exécuteur du pipeline catalogue" || echo "Compte déjà existant."

gcloud projects add-iam-policy-binding "${PROJET_ID}"   --member="serviceAccount:${SERVICE_ACCOUNT}"   --role="roles/storage.objectAdmin" --condition=None || true

echo "=== 2. Déploiement de la Cloud Function job-catalogue ==="
gcloud functions deploy job-catalogue   --gen2   --runtime=python311   --region="${REGION}"   --source=.   --entry-point=point_entree_http   --trigger-http   --no-allow-unauthenticated   --service-account="${SERVICE_ACCOUNT}"   --set-env-vars="BUCKET_CATALOGUE=${BUCKET_NAME},GCP_PROJECT=${PROJET_ID}"   --memory=256Mi   --timeout=120s

echo "=== Déploiement terminé avec succès ==="
