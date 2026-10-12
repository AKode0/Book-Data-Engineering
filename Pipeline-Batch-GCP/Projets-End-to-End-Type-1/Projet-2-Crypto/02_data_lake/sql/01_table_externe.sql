-- ==============================================================================
-- 02_data_lake/sql/01_table_externe.sql
-- Déclaration DDL explicite des tables externes Crypto
-- ==============================================================================
CREATE OR REPLACE EXTERNAL TABLE `entrepot_crypto.raw_crypto` (
  actif STRING,
  prix_usd FLOAT64,
  date_ingestion_utc STRING
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://data-lake-crypto-${PROJET_ID}/api_crypto/*']
);

CREATE OR REPLACE EXTERNAL TABLE `entrepot_crypto.raw_crypto_rejets` (
  actif STRING,
  prix_usd FLOAT64,
  date_ingestion_utc STRING,
  motif_rejet STRING,
  rejete_le_utc STRING
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://data-lake-crypto-${PROJET_ID}/api_crypto_rejets/*']
);
