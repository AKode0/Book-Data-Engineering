-- Instruction de fusion idempotente sur les cotations
MERGE `entrepot_crypto.clean_cotations` AS cible
-- Projection nettoye depuis la table externe
USING (
  -- Selection et conversion defensives des attributs bruts
  SELECT
    -- Conversion securisee du symbole d actif en chaine
    SAFE_CAST(actif AS STRING)                 AS actif,
    -- Conversion securisee du prix en nombre flottant
    SAFE_CAST(prix_usd AS FLOAT64)             AS prix_usd,
    -- Conversion securisee de l horodatage logique UTC en timestamp
    SAFE_CAST(date_ingestion_utc AS TIMESTAMP) AS mesure_le
  -- Source externe interrogeant directement Cloud Storage
  FROM `entrepot_crypto.raw_crypto`
  -- Elimination prealable des dates corrompues
  WHERE SAFE_CAST(date_ingestion_utc AS TIMESTAMP) IS NOT NULL
) AS source
-- Condition de correspondance sur la cle primaire composite
ON  cible.actif = source.actif
-- Egalite stricte sur l instant exact de cotation
AND cible.mesure_le = source.mesure_le
-- Clause appliquee uniquement si la donnee est absente
WHEN NOT MATCHED THEN
  -- Insertion des colonnes cibles
  INSERT (actif, prix_usd, mesure_le, charge_le)
  -- Valeurs issues de la source et horodatage de traitement
  VALUES (source.actif, source.prix_usd, source.mesure_le, CURRENT_TIMESTAMP());