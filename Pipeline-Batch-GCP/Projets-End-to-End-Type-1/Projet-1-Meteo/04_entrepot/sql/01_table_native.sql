-- La table propre. NATIVE, donc stockee par BigQuery, donc rapide.
-- Partitionnee par jour de mesure, groupee par ville.

CREATE TABLE IF NOT EXISTS `PROJET_ID.entrepot.meteo` (
  ville       STRING    NOT NULL,
  mesure_le   TIMESTAMP NOT NULL,
  latitude    FLOAT64,
  longitude   FLOAT64,
  temperature FLOAT64,
  vent_kmh    FLOAT64,
  fuseau      STRING,
  charge_le   TIMESTAMP NOT NULL,
  dt          DATE      NOT NULL
)
PARTITION BY DATE(mesure_le)
CLUSTER BY ville
OPTIONS (
  description = "Mesures meteo, une ligne par ville et par releve",
  require_partition_filter = true
);