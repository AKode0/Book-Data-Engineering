-- ==============================================================================
-- 04_entrepot/sql/03_audit.sql
-- Contrôles de qualité automatisés de la mobilité Vélib'
-- ==============================================================================

-- 1. Détection de valeurs de vélos ou bornes négatives
SELECT 'Vélos ou bornes négatifs' AS anomalie, COUNT(*) AS volume
FROM `entrepot_mobilite.stations_velib`
WHERE velos_disponibles < 0 OR bornes_libres < 0
HAVING COUNT(*) > 0

UNION ALL

-- 2. Détection d'incohérence volumétrique (somme vélos + bornes > capacité * 1.5)
SELECT 'Capacité incohérente (vélos + bornes > 1.5 * capacité)' AS anomalie, COUNT(*) AS volume
FROM `entrepot_mobilite.stations_velib`
WHERE capacite > 0 AND (velos_disponibles + bornes_libres) > (capacite * 1.5)
HAVING COUNT(*) > 0

UNION ALL

-- 3. Détection de doublons sur la clé composite (station_id, mesure_le)
SELECT 'Doublons sur clé composite (station_id, mesure_le)' AS anomalie, COUNT(*) AS volume
FROM (
  SELECT station_id, mesure_le
  FROM `entrepot_mobilite.stations_velib`
  GROUP BY station_id, mesure_le
  HAVING COUNT(*) > 1
)
HAVING COUNT(*) > 0;
