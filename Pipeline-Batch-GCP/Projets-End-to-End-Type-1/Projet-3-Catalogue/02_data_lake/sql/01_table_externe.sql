-- ==============================================================================
-- 02_data_lake/sql/01_table_externe.sql
-- Déclaration DDL explicite des tables externes
-- ==============================================================================
CREATE OR REPLACE EXTERNAL TABLE `entrepot_catalogue.raw_catalogue` (
  identifiant INT64,
  nom STRING,
  statut STRING,
  espece STRING,
  genre STRING,
  origine_nom STRING,
  date_ingestion_utc STRING
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://data-lake-catalogue-${PROJET_ID}/api_catalogue/*']
);

CREATE OR REPLACE EXTERNAL TABLE `entrepot_catalogue.raw_catalogue_rejets` (
  donnee_brute STRING,
  motif_rejet STRING,
  charge_le TIMESTAMP
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://data-lake-catalogue-${PROJET_ID}/api_catalogue_rejets/*']
);
