CREATE OR REPLACE VIEW `PROJET_ID.entrepot.v_meteo` AS
SELECT
  ville,
  mesure_le,
  DATE(mesure_le)                 AS jour,
  EXTRACT(HOUR FROM mesure_le)    AS heure,
  temperature,
  vent_kmh,
  charge_le
FROM `PROJET_ID.entrepot.meteo`
WHERE DATE(mesure_le) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY);