-- Chargement incrémental idempotent du catalogue
MERGE `entrepot_catalogue.table_catalogue` AS cible
USING (
  SELECT
    SAFE_CAST(identifiant AS INT64) AS identifiant,
    SAFE_CAST(nom AS STRING) AS nom,
    SAFE_CAST(statut AS STRING) AS statut,
    SAFE_CAST(espece AS STRING) AS espece,
    SAFE_CAST(genre AS STRING) AS genre,
    SAFE_CAST(origine AS STRING) AS origine,
    SAFE_CAST(dimension AS STRING) AS dimension,
    SAFE_CAST(date_ingestion_utc AS TIMESTAMP) AS date_ingestion_utc
  FROM `entrepot_catalogue.raw_catalogue`
  WHERE identifiant IS NOT NULL
    AND SAFE_CAST(date_ingestion_utc AS TIMESTAMP) IS NOT NULL
) AS source
ON cible.identifiant = source.identifiant
WHEN MATCHED THEN UPDATE SET
  nom = source.nom,
  statut = source.statut,
  espece = source.espece,
  genre = source.genre,
  origine = source.origine,
  dimension = source.dimension,
  date_ingestion_utc = source.date_ingestion_utc,
  charge_le = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT (
  identifiant, nom, statut, espece, genre, origine, dimension, date_ingestion_utc, charge_le
) VALUES (
  source.identifiant, source.nom, source.statut, source.espece, source.genre, source.origine, source.dimension, source.date_ingestion_utc, CURRENT_TIMESTAMP()
);
