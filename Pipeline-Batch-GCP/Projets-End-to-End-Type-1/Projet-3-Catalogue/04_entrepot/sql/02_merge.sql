MERGE `entrepot_catalogue.table_catalogue` AS cible
USING (
  SELECT
    SAFE_CAST(id AS STRING) AS cle_identifiant,
    SAFE_CAST(valeur AS FLOAT64) AS valeur_mesure,
    SAFE_CAST(date_utc AS TIMESTAMP) AS horodatage_mesure
  FROM `entrepot_catalogue.raw_catalogue`
  WHERE SAFE_CAST(date_utc AS TIMESTAMP) IS NOT NULL
) AS source
ON cible.cle_identifiant = source.cle_identifiant AND cible.horodatage_mesure = source.horodatage_mesure
WHEN NOT MATCHED THEN
  INSERT (cle_identifiant, valeur_mesure, horodatage_mesure, charge_le)
  VALUES (source.cle_identifiant, source.valeur_mesure, source.horodatage_mesure, CURRENT_TIMESTAMP());