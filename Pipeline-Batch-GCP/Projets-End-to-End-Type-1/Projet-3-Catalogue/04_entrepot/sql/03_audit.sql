-- Contrôles de qualité automatisés sur l'entrepôt catalogue
SELECT 'Identifiant manquant ou corrompu' AS anomalie, COUNT(*) AS volume
FROM `entrepot_catalogue.table_catalogue`
WHERE identifiant IS NULL
HAVING COUNT(*) > 0

UNION ALL

SELECT 'Doublons sur identifiant' AS anomalie, COUNT(*) AS volume
FROM (
  SELECT identifiant
  FROM `entrepot_catalogue.table_catalogue`
  GROUP BY identifiant
  HAVING COUNT(*) > 1
)
HAVING COUNT(*) > 0;
