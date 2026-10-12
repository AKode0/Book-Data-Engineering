-- ==============================================================================
-- 02_data_lake/sql/01_table_externe.sql
-- Déclaration DDL explicite des tables externes Crypto
-- ==============================================================================
CREATE OR REPLACE EXTERNAL TABLE `entrepot_crypto.raw_crypto` (
  actif STRING,
  prix_usd FLOAT64,
  mesure_le STRING,
  charge_le STRING
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://data-lake-crypto-${PROJET_ID}/api_crypto/*']
);

CREATE OR REPLACE EXTERNAL TABLE `entrepot_crypto.raw_crypto_rejets` (
  donnee_brute STRING,
  motif_rejet STRING,
  charge_le TIMESTAMP
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://data-lake-crypto-${PROJET_ID}/api_crypto_rejets/*']
);
