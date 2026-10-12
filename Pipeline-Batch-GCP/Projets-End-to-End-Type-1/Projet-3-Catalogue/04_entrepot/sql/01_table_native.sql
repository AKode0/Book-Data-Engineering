-- Table native du catalogue dédoublonnée, partitionnée et clusterisée.

CREATE TABLE IF NOT EXISTS `entrepot_catalogue.table_catalogue` (
  identifiant         INT64     NOT NULL,
  nom                 STRING    NOT NULL,
  statut              STRING,
  espece              STRING,
  genre               STRING,
  origine             STRING,
  dimension           STRING,
  date_ingestion_utc  TIMESTAMP NOT NULL,
  charge_le           TIMESTAMP NOT NULL
)
PARTITION BY DATE(date_ingestion_utc)
CLUSTER BY espece, statut
OPTIONS (
  description = "Catalogue de personnages dédoublonné et enrichi"
);
