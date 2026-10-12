-- ==============================================================================
-- 05_restitution/sql/01_vue_analytique.sql
-- Couche GOLD : Synthèse journalière météo prête pour Looker Studio
-- ==============================================================================
CREATE OR REPLACE VIEW `entrepot_meteo.vue_meteo_journaliere` AS
WITH agregat_jour AS (
  SELECT
    code_insee,
    ville,
    DATE(releve_le) AS date_releve,
    ROUND(AVG(temperature_celsius), 2) AS temp_moyenne_c,
    ROUND(MIN(temperature_celsius), 2) AS temp_minimale_c,
    ROUND(MAX(temperature_celsius), 2) AS temp_maximale_c,
    ROUND(SUM(precipitation_mm), 2) AS cumul_pluie_mm
  FROM `entrepot_meteo.releves_horaires`
  GROUP BY code_insee, ville, date_releve
)
SELECT
  code_insee,
  ville,
  date_releve,
  temp_moyenne_c,
  temp_minimale_c,
  temp_maximale_c,
  ROUND(temp_maximale_c - temp_minimale_c, 2) AS amplitude_thermique_c,
  cumul_pluie_mm,
  CASE 
    WHEN cumul_pluie_mm > 5.0 THEN 'Pluvieux'
    WHEN temp_maximale_c >= 25.0 THEN 'Chaud'
    WHEN temp_minimale_c <= 5.0 THEN 'Froid'
    ELSE 'Tempéré'
  END AS condition_dominante_jour,
  ROUND(AVG(temp_moyenne_c) OVER(PARTITION BY code_insee ORDER BY date_releve ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS moyenne_mobile_7j_c
FROM agregat_jour;
