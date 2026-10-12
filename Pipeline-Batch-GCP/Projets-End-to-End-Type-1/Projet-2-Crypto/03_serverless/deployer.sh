#!/usr/bin/env bash
# ==============================================================================
# Déploiement Cloud Functions Gen 2 - Pipeline Crypto
# ==============================================================================
set -euo pipefail

cd "$(dirname "$0")"

PROJET_ID=$(gcloud config get-value project)
BUCKET_CRYPTO="data-lake-crypto-${PROJET_ID}"
REGION="europe-west9"
SA_NAME="sa-executeur-crypto"
SERVICE_ACCOUNT="${SA_NAME}@${PROJET_ID}.iam.gserviceaccount.com"

echo "=== 1. Vérification et création du compte de service exécuteur ==="
gcloud iam service-accounts create "${SA_NAME}" \
  --display-name="Exécuteur du pipeline crypto" || echo "Compte déjà existant."

gcloud projects add-iam-policy-binding "${PROJET_ID}" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/storage.objectAdmin" --condition=None || true

echo "=== 2. Déploiement de la Cloud Function ingestion-crypto ==="
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
  --memory=256Mi \
  --timeout=120s

echo "=== Déploiement terminé avec succès ==="
