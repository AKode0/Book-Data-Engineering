CREATE OR REPLACE VIEW `entrepot_catalogue.vue_catalogue` AS
SELECT
  cle_identifiant,
  DATE(horodatage_mesure) AS date_mesure,
  valeur_mesure,
  ROUND(AVG(valeur_mesure) OVER(PARTITION BY cle_identifiant ORDER BY horodatage_mesure ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS moyenne_mobile_7j,
  horodatage_mesure
FROM `entrepot_catalogue.table_catalogue`;