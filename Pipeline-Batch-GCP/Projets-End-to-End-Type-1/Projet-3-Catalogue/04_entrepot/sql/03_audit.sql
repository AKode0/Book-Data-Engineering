SELECT 'Valeurs nulles ou corrompues' AS anomalie, COUNT(*) AS volume
FROM `entrepot_catalogue.table_catalogue`
WHERE valeur_mesure IS NULL
HAVING COUNT(*) > 0
UNION ALL
SELECT 'Doublons sur clé et horodatage', COUNT(*)
FROM (
  SELECT cle_identifiant, horodatage_mesure
  FROM `entrepot_catalogue.table_catalogue`
  GROUP BY cle_identifiant, horodatage_mesure
  HAVING COUNT(*) > 1
)
HAVING COUNT(*) > 0;
