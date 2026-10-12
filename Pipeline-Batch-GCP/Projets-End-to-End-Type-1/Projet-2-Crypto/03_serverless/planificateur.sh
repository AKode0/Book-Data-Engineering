#!/usr/bin/env bash
# ==============================================================================
# Planification Cloud Scheduler - Pipeline Crypto
# ==============================================================================
set -euo pipefail

PROJET_ID=$(gcloud config get-value project)
REGION="europe-west9"
SERVICE_ACCOUNT_TRIGGER="sa-declencheur-crypto@${PROJET_ID}.iam.gserviceaccount.com"

# Récupération de l'URL de la fonction déployée
URL_FONCTION=$(gcloud functions describe ingestion-crypto \
  --region="${REGION}" \
  --format='value(serviceConfig.uri)')

# Droit pour le déclencheur d'appeler Cloud Run (moteur sous-jacent de Gen 2)
gcloud run services add-iam-policy-binding ingestion-crypto \
  --region="${REGION}" \
  --member="serviceAccount:${SERVICE_ACCOUNT_TRIGGER}" \
  --role="roles/run.invoker"

echo "=== Création du job Cloud Scheduler (Toutes les heures) ==="
gcloud scheduler jobs create http job-ingestion-crypto-horaire \
  --location="${REGION}" \
  --schedule="0 * * * *" \
  --time-zone="Europe/Paris" \
  --uri="${URL_FONCTION}" \
  --http-method=GET \
  --oidc-service-account-email="${SERVICE_ACCOUNT_TRIGGER}" \
  --oidc-token-audience="${URL_FONCTION}" || echo "Job déjà existant."

echo "=== Planificateur configuré avec succès ==="
