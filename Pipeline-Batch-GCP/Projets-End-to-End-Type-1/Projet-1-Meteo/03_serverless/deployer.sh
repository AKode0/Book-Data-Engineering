#!/usr/bin/env bash
# ==============================================================================
# Déploiement Cloud Functions Gen 2 - Pipeline Météo
# ==============================================================================
set -euo pipefail

cd "$(dirname "$0")"

PROJET=$(gcloud config get-value project)
REGION="europe-west9"
FONCTION="job-meteo"
BUCKET="data-lake-meteo-${PROJET}"
SA_NAME="sa-pipeline"
SERVICE_ACCOUNT="${SA_NAME}@${PROJET}.iam.gserviceaccount.com"

echo "=== 1. Vérification et création du compte de service exécuteur ==="
gcloud iam service-accounts create "${SA_NAME}" \
  --display-name="Compte d execution Cloud Function Meteo" || echo "Compte déjà existant."

gcloud projects add-iam-policy-binding "${PROJET}" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/storage.objectAdmin" --condition=None || true

echo "=== 2. Déploiement de la Cloud Function ${FONCTION} ==="
gcloud functions deploy "${FONCTION}" \
  --gen2 \
  --region="${REGION}" \
  --runtime=python311 \
  --source=. \
  --entry-point=run_pipeline \
  --trigger-http \
  --no-allow-unauthenticated \
  --service-account="${SERVICE_ACCOUNT}" \
  --set-env-vars="BUCKET=${BUCKET},GCP_PROJECT=${PROJET},API_URL=https://api.open-meteo.com/v1/forecast" \
  --timeout=120s \
  --memory=256Mi

echo "=== Déploiement terminé avec succès ==="
