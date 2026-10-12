#!/usr/bin/env bash
set -euo pipefail

PROJET_ID=$(gcloud config get-value project)
BUCKET_NAME="data-lake-catalogue-${PROJET_ID}"
REGION="europe-west9"
SERVICE_ACCOUNT="sa-executeur-catalogue@${PROJET_ID}.iam.gserviceaccount.com"

echo "=== Déploiement de la Cloud Function job-catalogue ==="
gcloud functions deploy job-catalogue \
  --gen2 \
  --runtime=python312 \
  --region="${REGION}" \
  --source=. \
  --entry-point=point_entree_http \
  --trigger-http \
  --no-allow-unauthenticated \
  --service-account="${SERVICE_ACCOUNT}" \
  --set-env-vars="BUCKET_NOM=${BUCKET_NAME},GCP_PROJECT=${PROJET_ID}" \
  --memory=256Mi \
  --timeout=120s

echo "=== Déploiement terminé avec succès ==="