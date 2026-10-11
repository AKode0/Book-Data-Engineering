#!/bin/bash
# Deploiement du pipeline meteo. Relancable sans dommage.
set -e

PROJET=$(gcloud config get-value project)
REGION=europe-west9
FONCTION=job-meteo
BUCKET=data-lake-akf-2026

echo "--- deploiement de $FONCTION"
gcloud functions deploy $FONCTION \
  --gen2 \
  --region=$REGION \
  --runtime=python312 \
  --source=. \
  --entry-point=run_pipeline \
  --trigger-http \
  --no-allow-unauthenticated \
  --service-account="sa-pipeline@$PROJET.iam.gserviceaccount.com" \
  --set-env-vars="BUCKET=$BUCKET,API_URL=https://api.open-meteo.com/v1/forecast" \
  --timeout=120s \
  --memory=256Mi

echo "--- droit d'appel au seul compte du planificateur"
gcloud run services add-iam-policy-binding $FONCTION \
  --region=$REGION \
  --member="serviceAccount:sa-scheduler@$PROJET.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

URL=$(gcloud functions describe $FONCTION --region=$REGION --gen2 \
        --format='value(serviceConfig.uri)')
echo "--- url : $URL"