-- Verification 1 Controle des cours financiers negatifs ou nuls
SELECT 'Cours de crypto anormal négatif ou nul' AS anomalie, COUNT(*) AS volume
-- Interrogation de la table propre des cotations
FROM `entrepot_crypto.clean_cotations`
-- Filtrage sur les prix inferieurs ou egaux a zero
WHERE prix_usd <= 0
-- Alerte levee uniquement si des anomalies sont detectees
HAVING COUNT(*) > 0

-- Union des tests d integrite
UNION ALL

-- Verification 2 Controle des horodatages futurs
SELECT 'Mesure de cotation dans le futur', COUNT(*)
-- Interrogation de la table propre des cotations
FROM `entrepot_crypto.clean_cotations`
-- Filtrage sur les dates posterieures a l instant present
WHERE mesure_le > CURRENT_TIMESTAMP()
-- Alerte levee en cas de violation
HAVING COUNT(*) > 0

-- Union avec le controle des doublons
UNION ALL

-- Verification 3 Controle d unicite de la paire actif et horodatage
SELECT 'Présence de doublons sur la cotation', COUNT(*)
-- Sous-requete de regroupement sur la cle composite
FROM (
  -- Selection de la cle et comptage des doublons
  SELECT actif, mesure_le
  -- Lecture depuis la table propre
  FROM `entrepot_crypto.clean_cotations`
  -- Regroupement par actif et date de cotation
  GROUP BY actif, mesure_le
  -- Filtrage des occurrences strictement superieures a un
  HAVING COUNT(*) > 1
)
-- Alerte levee uniquement en presence de doublons
HAVING COUNT(*) > 0;