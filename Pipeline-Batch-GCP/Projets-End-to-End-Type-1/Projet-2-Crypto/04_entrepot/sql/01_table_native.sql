-- Creation de la table native des cotations crypto
CREATE TABLE IF NOT EXISTS `entrepot_crypto.clean_cotations` (
  -- Symbole ou identifiant de l actif financier
  actif           STRING    NOT NULL,
  -- Cours de cotation unitaire exprime en dollar USD
  prix_usd        FLOAT64   NOT NULL,
  -- Horodatage universel de la mesure transmis par la source
  mesure_le       TIMESTAMP NOT NULL,
  -- Horodatage universel de l insertion physique en entrepot
  charge_le       TIMESTAMP NOT NULL
)
-- Partitionnement temporel sur la date logique de cotation
PARTITION BY DATE(mesure_le)
-- Organisation en grappes par actif pour accelerer les filtres d analyse
CLUSTER BY actif;