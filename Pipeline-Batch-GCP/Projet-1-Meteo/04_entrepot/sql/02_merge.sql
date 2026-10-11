-- 02_merge.sql — chargement incremental de l'entrepot
-- Trois etages.
--   1. lu          lit UNE partition du lake, pas tout le lake
--   2. type        SAFE_CAST et SAFE.PARSE_TIMESTAMP, jamais CAST
--   3. dedoublonne un seul enregistrement par cle, le plus recent

DECLARE jour      DATE DEFAULT @run_date;
DECLARE borne_min DATE;
DECLARE borne_max DATE;

-- Les dates de mesure que ce lot peut toucher. Calculees AVANT le
-- MERGE, parce qu'un filtre de partition doit etre une constante au
-- moment ou BigQuery choisit les partitions a lire.
SET (borne_min, borne_max) = (
  SELECT AS STRUCT
    MIN(DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M', releve_le))),
    MAX(DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M', releve_le)))
  FROM `deft-smile-511110-q3.lake.raw_meteo`
  WHERE dt = jour
);

MERGE `deft-smile-511110-q3.entrepot.meteo` AS cible
USING (
  WITH lu AS (
    SELECT *
    FROM `deft-smile-511110-q3.lake.raw_meteo`
    WHERE dt = jour
  ),
  type AS (
    SELECT
      ville,
      -- L'API rend l'heure sans fuseau. Quand le champ `fuseau` vaut
      -- GMT, l'heure EST de l'UTC, et la lecture ci-dessous est juste.
      SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M', releve_le) AS mesure_le,
      SAFE_CAST(latitude    AS FLOAT64)   AS latitude,
      SAFE_CAST(longitude   AS FLOAT64)   AS longitude,
      SAFE_CAST(temperature AS FLOAT64)   AS temperature,
      SAFE_CAST(vent_kmh    AS FLOAT64)   AS vent_kmh,
      fuseau,
      SAFE_CAST(charge_le   AS TIMESTAMP) AS charge_le,
      dt
    FROM lu
  ),
  dedoublonne AS (
    SELECT * EXCEPT(rang)
    FROM (
      SELECT *,
             ROW_NUMBER() OVER (PARTITION BY ville, mesure_le
                                ORDER BY charge_le DESC) AS rang
      FROM type
      WHERE mesure_le IS NOT NULL     -- une date illisible ne rentre pas
        AND ville     IS NOT NULL
    )
    WHERE rang = 1
  )
  SELECT * FROM dedoublonne
) AS source
ON  cible.ville     = source.ville
AND cible.mesure_le = source.mesure_le
AND DATE(cible.mesure_le) BETWEEN borne_min AND borne_max

WHEN MATCHED THEN UPDATE SET
  latitude    = source.latitude,
  longitude   = source.longitude,
  temperature = source.temperature,
  vent_kmh    = source.vent_kmh,
  fuseau      = source.fuseau,
  charge_le   = source.charge_le,
  dt          = source.dt

WHEN NOT MATCHED THEN INSERT
  (ville, mesure_le, latitude, longitude, temperature, vent_kmh,
   fuseau, charge_le, dt)
VALUES
  (source.ville, source.mesure_le, source.latitude, source.longitude,
   source.temperature, source.vent_kmh, source.fuseau,
   source.charge_le, source.dt);