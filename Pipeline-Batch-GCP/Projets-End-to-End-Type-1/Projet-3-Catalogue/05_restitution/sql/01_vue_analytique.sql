-- Vue analytique Looker Studio : répartition démographique par espèce, statut et genre
CREATE OR REPLACE VIEW `entrepot_catalogue.vue_catalogue` AS
SELECT
  espece,
  statut,
  genre,
  COUNT(*) AS total_personnages,
  COUNT(DISTINCT origine) AS total_mondes_origine,
  CURRENT_TIMESTAMP() AS vue_calculee_le
FROM `entrepot_catalogue.table_catalogue`
GROUP BY espece, statut, genre;
