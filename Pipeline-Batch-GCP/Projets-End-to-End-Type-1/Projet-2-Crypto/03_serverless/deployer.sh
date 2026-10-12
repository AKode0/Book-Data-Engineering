#!/usr/bin/env bash
# ==============================================================================
# Déploiement Cloud Functions Gen 2 - Pipeline Crypto (avec Secret Manager)
# ==============================================================================
set -euo pipefail

cd "$(dirname "$0")"

PROJET_ID=$(gcloud config get-value project)
BUCKET_CRYPTO="data-lake-crypto-${PROJET_ID}"
REGION="europe-west9"
FONCTION="ingestion-crypto"
SA_NAME="sa-executeur-crypto"
SERVICE_ACCOUNT="${SA_NAME}@${PROJET_ID}.iam.gserviceaccount.com"
SECRET_NAME="cle-coingecko-api"

echo "=== 1. Activation des APIs Google Cloud requises ==="
gcloud services enable \
  cloudfunctions.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com || true

echo "=== 2. Vérification et création du secret dans Secret Manager ==="
gcloud secrets create "${SECRET_NAME}" --replication-policy="automatic" || echo "Secret ${SECRET_NAME} déjà créé."

# Ajout d'une version initiale si aucune version n'est active
if ! gcloud secrets versions describe latest --secret="${SECRET_NAME}" &>/dev/null; then
  echo "Ajout d'une version initiale au secret ${SECRET_NAME}..."
  printf '%s' "${COINGECKO_API_KEY:-CG-DEMO-DEFAULT-KEY}" | gcloud secrets versions add "${SECRET_NAME}" --data-file=-
fi

echo "=== 3. Vérification du Bucket Cloud Storage ==="
gcloud storage buckets create "gs://${BUCKET_CRYPTO}" \
  --location="${REGION}" \
  --uniform-bucket-level-access \
  --public-access-prevention || echo "Bucket déjà existant."

echo "=== 4. Vérification et création du compte de service exécuteur ==="
gcloud iam service-accounts create "${SA_NAME}" \
  --display-name="Exécuteur du pipeline crypto" || echo "Compte déjà existant."

echo "=== 5. Attribution des privilèges IAM (Storage + Secret Manager) ==="
gcloud projects add-iam-policy-binding "${PROJET_ID}" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/storage.objectAdmin" --condition=None || true

gcloud projects add-iam-policy-binding "${PROJET_ID}" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor" --condition=None || true

echo "=== 6. Déploiement de la Cloud Function ${FONCTION} ==="
gcloud functions deploy "${FONCTION}" \
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

URL=$(gcloud functions describe "${FONCTION}" --region="${REGION}" --gen2 --format='value(serviceConfig.uri)')
echo "=== Déploiement terminé avec succès. URL : ${URL} ==="
