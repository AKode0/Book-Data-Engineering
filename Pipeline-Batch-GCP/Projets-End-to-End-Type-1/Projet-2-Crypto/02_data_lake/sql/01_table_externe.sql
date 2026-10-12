-- ==============================================================================
-- 02_data_lake/sql/01_table_externe.sql
-- Déclaration DDL explicite des tables externes Crypto
-- ==============================================================================
CREATE OR REPLACE EXTERNAL TABLE `entrepot_crypto.raw_crypto`
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://data-lake-crypto-*/api_crypto/*']
);

CREATE OR REPLACE EXTERNAL TABLE `entrepot_crypto.raw_crypto_rejets` (
  donnee_brute STRING,
  motif_rejet STRING,
  charge_le TIMESTAMP
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://data-lake-crypto-*/api_crypto_rejets/*']
);
