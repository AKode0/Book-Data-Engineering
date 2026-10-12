#!/usr/bin/env bash
# ==============================================================================
# Déploiement Cloud Functions Gen 2 - Pipeline Crypto
# ==============================================================================
set -euo pipefail

PROJET_ID=$(gcloud config get-value project)
BUCKET_CRYPTO="data-lake-crypto-${PROJET_ID}"
REGION="europe-west9"
SERVICE_ACCOUNT="sa-executeur-crypto@${PROJET_ID}.iam.gserviceaccount.com"

echo "=== Déploiement de la Cloud Function ingestion-crypto ==="
gcloud functions deploy ingestion-crypto \
  --gen2 \
  --runtime=python311 \
  --region="${REGION}" \
  --source=. \
  --entry-point=point_entree_http \
  --trigger-http \
  --no-allow-unauthenticated \
  --service-account="${SERVICE_ACCOUNT}" \
  --set-env-vars="GCP_PROJECT=${PROJET_ID},BUCKET_CRYPTO=${BUCKET_CRYPTO}" \
  --memory=512Mi \
  --timeout=300s

echo "=== Déploiement terminé avec succès ==="
