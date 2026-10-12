-- Chargement incrémental idempotent de la table native depuis la table externe.
MERGE `entrepot_meteo.releves_horaires` AS cible
USING (
  WITH lu AS (
    SELECT *
    FROM `entrepot_meteo.raw_meteo`
    WHERE dt = CURRENT_DATE()
  ),
  type AS (
    SELECT
      ville,
      SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M', releve_le) AS mesure_le,
      SAFE_CAST(latitude    AS FLOAT64)   AS latitude,
      SAFE_CAST(longitude   AS FLOAT64)   AS longitude,
      SAFE_CAST(temperature AS FLOAT64)   AS temperature,
      SAFE_CAST(vent_kmh    AS FLOAT64)   AS vent_kmh,
      fuseau,
      CURRENT_TIMESTAMP()                 AS charge_le,
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
      WHERE mesure_le IS NOT NULL
        AND ville IS NOT NULL
    )
    WHERE rang = 1
  )
  SELECT * FROM dedoublonne
) AS source
ON  cible.ville     = source.ville
AND cible.mesure_le = source.mesure_le
AND cible.dt        = source.dt

WHEN MATCHED THEN UPDATE SET
  latitude    = source.latitude,
  longitude   = source.longitude,
  temperature = source.temperature,
  vent_kmh    = source.vent_kmh,
  fuseau      = source.fuseau,
  charge_le   = source.charge_le

WHEN NOT MATCHED THEN INSERT
  (ville, mesure_le, latitude, longitude, temperature, vent_kmh,
   fuseau, charge_le, dt)
VALUES
  (source.ville, source.mesure_le, source.latitude, source.longitude,
   source.temperature, source.vent_kmh, source.fuseau,
   source.charge_le, source.dt);
