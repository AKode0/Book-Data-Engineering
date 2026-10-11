-- Zone brute. BigQuery lit les fichiers du bucket, sans les copier.
-- Le dossier dt=AAAA-MM-JJ devient une COLONNE de partition.

CREATE OR REPLACE EXTERNAL TABLE `PROJET_ID.lake.raw_meteo` (
  ville       STRING,
  latitude    FLOAT64,
  longitude   FLOAT64,
  temperature FLOAT64,
  vent_kmh    FLOAT64,
  releve_le   STRING,     -- texte, l'API le rend sans fuseau
  fuseau      STRING,
  charge_le   STRING      -- texte ici, TIMESTAMP au module 4
)
WITH PARTITION COLUMNS (
  dt DATE
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://data-lake-akf-2026/raw/meteo/*'],
  hive_partition_uri_prefix = 'gs://data-lake-akf-2026/raw/meteo',
  require_hive_partition_filter = true
);

-- Zone de rejets. Meme principe, autre dossier.
CREATE OR REPLACE EXTERNAL TABLE `PROJET_ID.lake.rejets_meteo` (
  ville     STRING,
  motif     STRING,
  charge_le STRING,
  brut      STRING        -- la ligne d'origine, en texte
)
WITH PARTITION COLUMNS (
  dt DATE
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://data-lake-akf-2026/rejets/meteo/*'],
  hive_partition_uri_prefix = 'gs://data-lake-akf-2026/rejets/meteo',
  require_hive_partition_filter = false
);

