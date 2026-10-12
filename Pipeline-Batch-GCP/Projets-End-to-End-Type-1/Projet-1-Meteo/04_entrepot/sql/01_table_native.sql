-- Table native conforme, partitionnée et clusterisée pour des requêtes rapides et économiques.

CREATE TABLE IF NOT EXISTS `entrepot_meteo.releves_horaires` (
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
PARTITION BY dt
CLUSTER BY ville
OPTIONS (
  description = "Mesures météo dédoublonnées et conformes, partitionnées par jour"
);
