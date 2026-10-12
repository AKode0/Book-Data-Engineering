-- ==============================================================================
-- 04_entrepot/sql/02_merge.sql
-- Fusion incrémentale idempotente sur clé composite (station_id, mesure_le)
-- ==============================================================================
MERGE `entrepot_mobilite.stations_velib` AS cible
USING (
  SELECT
    SAFE_CAST(station_id AS STRING)                 AS station_id,
    SAFE_CAST(nom_station AS STRING)                AS nom_station,
    SAFE_CAST(commune AS STRING)                    AS commune,
    SAFE_CAST(capacite AS INT64)                    AS capacite,
    SAFE_CAST(velos_disponibles AS INT64)           AS velos_disponibles,
    SAFE_CAST(bornes_libres AS INT64)               AS bornes_libres,
    SAFE_CAST(en_service AS BOOL)                   AS en_service,
    SAFE_CAST(mesure_le AS TIMESTAMP)               AS mesure_le
  FROM `entrepot_mobilite.raw_velib`
  WHERE station_id IS NOT NULL
    AND SAFE_CAST(mesure_le AS TIMESTAMP) IS NOT NULL
) AS source
ON  cible.station_id = source.station_id
AND cible.mesure_le  = source.mesure_le

WHEN MATCHED THEN UPDATE SET
  nom_station       = source.nom_station,
  commune           = source.commune,
  capacite          = source.capacite,
  velos_disponibles = source.velos_disponibles,
  bornes_libres     = source.bornes_libres,
  en_service        = source.en_service,
  charge_le         = CURRENT_TIMESTAMP()

WHEN NOT MATCHED THEN INSERT (
  station_id, nom_station, commune, capacite, velos_disponibles, bornes_libres, en_service, mesure_le, charge_le
) VALUES (
  source.station_id, source.nom_station, source.commune, source.capacite, source.velos_disponibles, source.bornes_libres, source.en_service, source.mesure_le, CURRENT_TIMESTAMP()
);
