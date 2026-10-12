-- ==============================================================================
-- 05_restitution/sql/01_vue_analytique.sql
-- Vue analytique Gold pour Looker Studio : Supervision de la disponibilité Vélib'
-- ==============================================================================
CREATE OR REPLACE VIEW `entrepot_mobilite.vue_mobilite_temps_reel` AS
WITH stations_recentes AS (
  SELECT
    station_id,
    nom_station,
    commune,
    capacite,
    velos_disponibles,
    bornes_libres,
    en_service,
    mesure_le,
    ROW_NUMBER() OVER(PARTITION BY station_id ORDER BY mesure_le DESC) AS rang
  FROM `entrepot_mobilite.stations_velib`
)
SELECT
  commune,
  COUNT(station_id) AS total_stations,
  SUM(capacite) AS capacite_totale,
  SUM(velos_disponibles) AS velos_disponibles_total,
  SUM(bornes_libres) AS bornes_libres_total,
  ROUND(SAFE_DIVIDE(SUM(velos_disponibles), SUM(capacite)) * 100, 2) AS taux_remplissage_pct,
  COUNTIF(velos_disponibles = 0 AND en_service = TRUE) AS stations_vides_alerte,
  COUNTIF(bornes_libres = 0 AND en_service = TRUE) AS stations_saturees_alerte,
  CURRENT_TIMESTAMP() AS vue_calculee_le
FROM stations_recentes
WHERE rang = 1
GROUP BY commune;
