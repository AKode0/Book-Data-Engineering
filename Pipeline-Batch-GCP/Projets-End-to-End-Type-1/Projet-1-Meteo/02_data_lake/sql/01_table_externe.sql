-- Zone brute : BigQuery interroge directement les fichiers NDJSON sur Cloud Storage.
-- La partition Hive dt=AAAA-MM-JJ est automatiquement reconnue comme colonne.

CREATE OR REPLACE EXTERNAL TABLE `entrepot_meteo.raw_meteo` (
  ville       STRING,
  latitude    FLOAT64,
  longitude   FLOAT64,
  temperature FLOAT64,
  vent_kmh    FLOAT64,
  releve_le   STRING,
  fuseau      STRING,
  charge_le   STRING
)
WITH PARTITION COLUMNS (
  dt DATE
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://data-lake-meteo-${PROJET_ID}/raw/meteo/*'],
  hive_partition_uri_prefix = 'gs://data-lake-meteo-${PROJET_ID}/raw/meteo',
  require_hive_partition_filter = false
);

CREATE OR REPLACE EXTERNAL TABLE `entrepot_meteo.rejets_meteo` (
  ville     STRING,
  motif     STRING,
  charge_le STRING,
  brut      STRING
)
WITH PARTITION COLUMNS (
  dt DATE
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://data-lake-meteo-${PROJET_ID}/rejets/meteo/*'],
  hive_partition_uri_prefix = 'gs://data-lake-meteo-${PROJET_ID}/rejets/meteo',
  require_hive_partition_filter = false
);
