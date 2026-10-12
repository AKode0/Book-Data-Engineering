#!/usr/bin/env bash
set -euo pipefail

PROJET_ID=$(gcloud config get-value project)
REGION="europe-west9"
SERVICE_ACCOUNT_TRIGGER="sa-declencheur-catalogue@${PROJET_ID}.iam.gserviceaccount.com"

URL_FONCTION=$(gcloud functions describe job-catalogue \
  --region="${REGION}" \
  --format='value(serviceConfig.uri)')

echo "=== Attribution du rôle d'appel Cloud Run ==="
gcloud run services add-iam-policy-binding job-catalogue \
  --region="${REGION}" \
  --member="serviceAccount:${SERVICE_ACCOUNT_TRIGGER}" \
  --role="roles/run.invoker"

echo "=== Création du job Cloud Scheduler ==="
gcloud scheduler jobs create http job-catalogue-quotidien \
  --location="${REGION}" \
  --schedule="0 4 * * *" \
  --time-zone="Europe/Paris" \
  --uri="${URL_FONCTION}" \
  --http-method=GET \
  --oidc-service-account-email="${SERVICE_ACCOUNT_TRIGGER}" \
  --oidc-token-audience="${URL_FONCTION}" || echo "Job déjà existant."

echo "=== Planificateur configuré avec succès ==="