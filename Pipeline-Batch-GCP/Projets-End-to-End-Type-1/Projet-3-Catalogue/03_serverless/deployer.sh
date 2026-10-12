#!/usr/bin/env bash
# ==============================================================================
# Déploiement Cloud Functions Gen 2 - Pipeline Catalogue
# ==============================================================================
set -euo pipefail

cd "$(dirname "$0")"

PROJET_ID=$(gcloud config get-value project)
BUCKET_NAME="data-lake-catalogue-${PROJET_ID}"
REGION="europe-west9"
FONCTION="job-catalogue"
SA_NAME="sa-executeur-catalogue"
SERVICE_ACCOUNT="${SA_NAME}@${PROJET_ID}.iam.gserviceaccount.com"

echo "=== 1. Activation des APIs Google Cloud requises ==="
gcloud services enable \
  cloudfunctions.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com || true

echo "=== 2. Vérification du Bucket Cloud Storage ==="
gcloud storage buckets create "gs://${BUCKET_NAME}" \
  --location="${REGION}" \
  --uniform-bucket-level-access \
  --public-access-prevention || echo "Bucket déjà existant."

echo "=== 3. Vérification et création du compte de service exécuteur ==="
gcloud iam service-accounts create "${SA_NAME}" \
  --display-name="Exécuteur du pipeline catalogue" || echo "Compte déjà existant."

gcloud projects add-iam-policy-binding "${PROJET_ID}" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/storage.objectAdmin" --condition=None || true

echo "=== 4. Déploiement de la Cloud Function ${FONCTION} ==="
gcloud functions deploy "${FONCTION}" \
  --gen2 \
  --runtime=python311 \
  --region="${REGION}" \
  --source=. \
  --entry-point=point_entree_http \
  --trigger-http \
  --no-allow-unauthenticated \
  --service-account="${SERVICE_ACCOUNT}" \
  --set-env-vars="BUCKET_CATALOGUE=${BUCKET_NAME},GCP_PROJECT=${PROJET_ID}" \
  --memory=256Mi \
  --timeout=120s

URL=$(gcloud functions describe "${FONCTION}" --region="${REGION}" --gen2 --format='value(serviceConfig.uri)')
echo "=== Déploiement terminé avec succès. URL : ${URL} ==="
