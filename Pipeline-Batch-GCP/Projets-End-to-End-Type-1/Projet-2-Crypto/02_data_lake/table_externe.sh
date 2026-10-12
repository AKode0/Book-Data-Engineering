#!/usr/bin/env bash
# ==============================================================================
# Automatisation Data Lake & Tables Externes - Projet 2 : Crypto
# ==============================================================================
set -euo pipefail

PROJET_ID=$(gcloud config get-value project)
BUCKET_CRYPTO="data-lake-crypto-${PROJET_ID}"
REGION="europe-west9"
DATASET="entrepot_crypto"

echo "=== 1. Création du Bucket Cloud Storage ==="
gcloud storage buckets create "gs://${BUCKET_CRYPTO}"   --location="${REGION}"   --uniform-bucket-level-access   --public-access-prevention || echo "Bucket déjà existant."

echo "=== 2. Création du Dataset BigQuery ==="
bq --location="${REGION}" mk --dataset "${PROJET_ID}:${DATASET}" || echo "Dataset déjà existant."

echo "=== 3. Application du DDL des tables externes ==="
sed "s/\${PROJET_ID}/$PROJET_ID/g" 02_data_lake/sql/01_table_externe.sql | bq query --use_legacy_sql=false

echo "=== Data Lake initialisé avec succès ==="
