CREATE TABLE IF NOT EXISTS `entrepot_catalogue.table_catalogue` (
  cle_identifiant STRING NOT NULL,
  valeur_mesure FLOAT64 NOT NULL,
  horodatage_mesure TIMESTAMP NOT NULL,
  charge_le TIMESTAMP NOT NULL
)
PARTITION BY DATE(horodatage_mesure)
CLUSTER BY cle_identifiant;