-- ==============================================================================
-- Couche GOLD : Vue analytique agrégée pour Looker Studio
-- ==============================================================================
CREATE OR REPLACE VIEW `entrepot_meteo.vue_meteo_journaliere` AS
WITH agregat_jour AS (
  SELECT
    ville,
    dt AS date_releve,
    ROUND(AVG(temperature), 2) AS temp_moyenne_c,
    ROUND(MIN(temperature), 2) AS temp_minimale_c,
    ROUND(MAX(temperature), 2) AS temp_maximale_c,
    ROUND(AVG(vent_kmh), 2)    AS vent_moyen_kmh
  FROM `entrepot_meteo.releves_horaires`
  GROUP BY ville, date_releve
)
SELECT
  ville,
  date_releve,
  temp_moyenne_c,
  temp_minimale_c,
  temp_maximale_c,
  ROUND(temp_maximale_c - temp_minimale_c, 2) AS amplitude_thermique_c,
  vent_moyen_kmh,
  CASE 
    WHEN temp_maximale_c >= 25.0 THEN 'Chaud'
    WHEN temp_minimale_c <= 5.0 THEN 'Froid'
    ELSE 'Tempéré'
  END AS condition_dominante_jour,
  ROUND(AVG(temp_moyenne_c) OVER(PARTITION BY ville ORDER BY date_releve ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS moyenne_mobile_7j_c
FROM agregat_jour;
