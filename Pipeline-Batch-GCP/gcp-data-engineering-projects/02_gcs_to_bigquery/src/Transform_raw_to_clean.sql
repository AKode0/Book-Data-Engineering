-- On crée une table native BigQuery (ou on la remplace si elle existe déjà)
CREATE OR REPLACE TABLE `meteo_data_warehouse.clean_weather` AS

SELECT
  -- On nettoie et on force les types de données (CAST)
  ville,
  CAST(latitude AS FLOAT64) AS latitude,
  CAST(longitude AS FLOAT64) AS longitude,
  CAST(temperature_celsius AS FLOAT64) AS temperature,
  CAST(windspeed_kmh AS FLOAT64) AS vent_kmh,
  CAST(ingestion_timestamp_utc AS TIMESTAMP) AS date_ingestion_utc
  
FROM
  `meteo_data_warehouse.raw_weather`;


