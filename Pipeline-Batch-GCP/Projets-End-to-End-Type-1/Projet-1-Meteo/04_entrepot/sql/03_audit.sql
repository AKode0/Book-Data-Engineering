-- ==============================================================================
-- 04_entrepot/sql/03_audit.sql
-- Contrôles de qualité des relevés météo
-- ==============================================================================
-- 1. Contrôle des températures aberrantes
SELECT 'Température aberrante (< -60°C ou > 65°C)' AS anomalie, COUNT(*) AS volume
FROM `entrepot_meteo.releves_horaires`
WHERE temperature_celsius < -60.0 OR temperature_celsius > 65.0
HAVING COUNT(*) > 0

UNION ALL

-- 2. Contrôle d'unicité (code_insee + releve_le)
SELECT 'Doublons sur releve_horaire', COUNT(*)
FROM (
  SELECT code_insee, releve_le
  FROM `entrepot_meteo.releves_horaires`
  GROUP BY code_insee, releve_le
  HAVING COUNT(*) > 1
)
HAVING COUNT(*) > 0;
