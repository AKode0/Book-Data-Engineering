#!/usr/bin/env bash
# ==============================================================================
# Ordonnancement Cloud Scheduler - Pipeline Catalogue
# ==============================================================================
set -euo pipefail

cd "$(dirname "$0")"

PROJET_ID=$(gcloud config get-value project)
REGION="europe-west9"
SA_TRIGGER_NAME="sa-declencheur-catalogue"
SERVICE_ACCOUNT_TRIGGER="${SA_TRIGGER_NAME}@${PROJET_ID}.iam.gserviceaccount.com"

echo "=== 1. Vérification du compte de service déclencheur ==="
gcloud iam service-accounts create "${SA_TRIGGER_NAME}"   --display-name="Déclencheur planifié du catalogue" || echo "Compte déjà existant."

echo "=== 2. Récupération de l'URL de la Cloud Function ==="
URL_FONCTION=$(gcloud functions describe job-catalogue   --region="${REGION}"   --format='value(serviceConfig.uri)')

echo "=== 3. Attribution du rôle d'appel Cloud Run ==="
gcloud run services add-iam-policy-binding job-catalogue   --region="${REGION}"   --member="serviceAccount:${SERVICE_ACCOUNT_TRIGGER}"   --role="roles/run.invoker"

echo "=== 4. Création du job Cloud Scheduler ==="
gcloud scheduler jobs create http job-catalogue-quotidien   --location="${REGION}"   --schedule="0 4 * * *"   --time-zone="Europe/Paris"   --uri="${URL_FONCTION}"   --http-method=GET   --oidc-service-account-email="${SERVICE_ACCOUNT_TRIGGER}"   --oidc-token-audience="${URL_FONCTION}" || echo "Job déjà existant."

echo "=== Planificateur configuré avec succès ==="
