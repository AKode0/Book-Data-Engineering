-- ==============================================================================
-- 02_data_lake/sql/01_table_externe.sql
-- Déclaration DDL explicite des tables externes Vélib'
-- ==============================================================================
CREATE OR REPLACE EXTERNAL TABLE `entrepot_mobilite.raw_velib` (
  station_id STRING,
  nom_station STRING,
  commune STRING,
  capacite INT64,
  velos_disponibles INT64,
  bornes_libres INT64,
  en_service BOOL,
  mesure_le STRING,
  date_ingestion_utc STRING
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://data-lake-mobilite-${PROJET_ID}/api_mobilite/*']
);

CREATE OR REPLACE EXTERNAL TABLE `entrepot_mobilite.raw_velib_rejets` (
  station_id STRING,
  nom_station STRING,
  commune STRING,
  capacite INT64,
  velos_disponibles INT64,
  bornes_libres INT64,
  en_service BOOL,
  mesure_le STRING,
  date_ingestion_utc STRING,
  motif_rejet STRING,
  rejete_le_utc STRING
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://data-lake-mobilite-${PROJET_ID}/api_mobilite_rejets/*']
);
