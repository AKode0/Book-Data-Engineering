-- ==============================================================================
-- Contrôles de qualité des relevés météo en entrepôt
-- ==============================================================================

-- 1. Contrôle des températures aberrantes (< -80°C ou > 60°C)
SELECT 'Température aberrante (< -80°C ou > 60°C)' AS anomalie, COUNT(*) AS volume
FROM `entrepot_meteo.releves_horaires`
WHERE temperature < -80.0 OR temperature > 60.0
HAVING COUNT(*) > 0

UNION ALL

-- 2. Contrôle des valeurs nulles sur champs critiques
SELECT 'Valeur nulle sur ville ou mesure_le' AS anomalie, COUNT(*) AS volume
FROM `entrepot_meteo.releves_horaires`
WHERE ville IS NULL OR mesure_le IS NULL
HAVING COUNT(*) > 0

UNION ALL

-- 3. Contrôle d'unicité (ville + mesure_le)
SELECT 'Doublons sur (ville, mesure_le)' AS anomalie, COUNT(*) AS volume
FROM (
  SELECT ville, mesure_le
  FROM `entrepot_meteo.releves_horaires`
  GROUP BY ville, mesure_le
  HAVING COUNT(*) > 1
)
HAVING COUNT(*) > 0;
