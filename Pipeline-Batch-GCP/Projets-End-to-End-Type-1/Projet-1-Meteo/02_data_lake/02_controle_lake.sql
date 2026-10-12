-- 1. COMBIEN DE JOURS SONT DANS LE LAKE
-- Doit augmenter de 1 par jour. Si ca reste a 1, le depot ecrase
-- toujours le meme chemin, donc le jour logique ne bouge pas.
SELECT COUNT(DISTINCT dt) AS jours, MIN(dt) AS premier, MAX(dt) AS dernier
FROM `PROJET_ID.lake.raw_meteo`
WHERE dt BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
             AND CURRENT_DATE();

-- 2. QUEL FICHIER PORTE QUELLE LIGNE
-- _FILE_NAME est une pseudo-colonne des tables externes. C'est le seul
-- moyen de savoir d'ou vient une ligne quand un chiffre surprend.
SELECT _FILE_NAME AS fichier, COUNT(*) AS lignes
FROM `PROJET_ID.lake.raw_meteo`
WHERE dt BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
             AND CURRENT_DATE()
GROUP BY fichier
ORDER BY fichier DESC;

-- 3. LES REJETS DU JOUR, PAR MOTIF
-- Un motif qui explose signale une derive de schema, pas des donnees
-- sales.
SELECT dt, motif, COUNT(*) AS n
FROM `PROJET_ID.lake.rejets_meteo`
WHERE dt = CURRENT_DATE()
GROUP BY dt, motif
ORDER BY n DESC;