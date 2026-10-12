-- ==============================================================================
-- 04_entrepot/sql/01_table_native.sql
-- Table native BigQuery : état des stations Vélib' partitionné et clusterisé
-- ==============================================================================

-- 1. Table d'état du filigrane d'ingestion CDC
CREATE TABLE IF NOT EXISTS `entrepot_mobilite.filigrane_etat` (
  identifiant_flux  STRING NOT NULL,
  dernier_succes    TIMESTAMP NOT NULL,
  actualise_le      TIMESTAMP NOT NULL
);

-- 2. Table native des stations conforme
CREATE TABLE IF NOT EXISTS `entrepot_mobilite.stations_velib` (
  station_id        STRING    NOT NULL,
  nom_station       STRING    NOT NULL,
  commune           STRING,
  capacite          INT64,
  velos_disponibles INT64     NOT NULL,
  bornes_libres     INT64     NOT NULL,
  en_service        BOOL      NOT NULL,
  mesure_le         TIMESTAMP NOT NULL,
  charge_le         TIMESTAMP NOT NULL
)
PARTITION BY DATE(mesure_le)
CLUSTER BY commune, station_id
OPTIONS (
  description = "Disponibilité des stations Vélib' en temps réel dédoublonnée"
);
