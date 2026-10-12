-- ==============================================================================
-- 05_restitution/sql/01_vue_analytique.sql
-- Couche GOLD : Métriques calculées prêtes pour Looker Studio
-- ==============================================================================
CREATE OR REPLACE VIEW `entrepot_crypto.vue_cotations_marche` AS
WITH base AS (
  SELECT
    actif,
    prix_usd,
    mesure_le,
    DATE(mesure_le) AS date_mesure,
    TIME(mesure_le) AS heure_mesure,
    LAG(prix_usd) OVER (PARTITION BY actif ORDER BY mesure_le ASC) AS prix_precedent_usd,
    SUM(prix_usd) OVER (PARTITION BY mesure_le) AS valeur_panier_instantane_usd
  FROM `entrepot_crypto.clean_cotations`
)
SELECT
  date_mesure,
  heure_mesure,
  actif,
  prix_usd,
  prix_precedent_usd,
  ROUND(SAFE_DIVIDE(prix_usd - prix_precedent_usd, prix_precedent_usd) * 100, 4) AS variation_precedente_pourcent,
  ROUND(SAFE_DIVIDE(prix_usd, valeur_panier_instantane_usd) * 100, 2) AS poids_dans_panier_pourcent,
  CASE
    WHEN prix_precedent_usd IS NULL THEN 'Premier Relevé'
    WHEN prix_usd > prix_precedent_usd THEN 'Hausse'
    WHEN prix_usd < prix_precedent_usd THEN 'Baisse'
    ELSE 'Stable'
  END AS tendance_instantanee,
  mesure_le
FROM base;
