# Importation du module standard json pour la manipulation des structures
import json
# Importation du module os pour l extraction des variables d environnement
import os
# Importation du module time pour les temporisations de securite reseau
import time
# Importation des utilitaires temporels pour fixer les horodatages stricts
from datetime import datetime, timezone

# Importation de requests pour l emission des requetes HTTP distantes
import requests
# Importation du client officiel Google Cloud BigQuery pour la table de filigrane
from google.cloud import bigquery
# Importation du client officiel Google Cloud Storage pour le stockage objet
from google.cloud import storage

# Identifiant du projet Google Cloud courant
PROJET_ID = os.environ.get("GCP_PROJECT", os.environ.get("PROJET_ID", "deft-smile-511110-q3"))
# Nom du compartiment de stockage cible
BUCKET_NOM = os.environ.get("BUCKET_MOBILITE", f"data-lake-mobilite-{PROJET_ID}")
# Identifiant unique du flux pour la table de filigrane
FLUX_ID = "stations_velib"
# URL officielle de l API ouverte de disponibilite Velib de Paris
API_URL = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records"
# Prefixe du dossier logique sur Cloud Storage
PREFIXE_STOCKAGE = "api_mobilite"
# Plafond maximal d iterations pour interdire toute boucle infinie
LIMITE_PAGES_MAX = 50
# Taille du lot par requete pour la pagination par offset
TAILLE_LOT = 100
# Volume de reference attendu de stations ouvertes
VOLUME_ATTENDU = 1400
# Marge de tolerance volumetrique autorisee a vingt pour cent
TOLERANCE_VOLUME = 0.20


# Fonction de controle volumetrique appliquee sur les lots collectes
def controler_volume(volume_recu):
    borne_min = VOLUME_ATTENDU * (1.0 - TOLERANCE_VOLUME)
    borne_max = VOLUME_ATTENDU * (1.0 + TOLERANCE_VOLUME)
    if volume_recu < borne_min:
        return False, f"Alerte lot partiel reduit {volume_recu} recu plancher {int(borne_min)}"
    if volume_recu > borne_max:
        return False, f"Alerte lot gonfle {volume_recu} recu plafond {int(borne_max)}"
    return True, f"Volume conforme avec {volume_recu} stations"


# Fonction de recuperation du dernier horodatage valide depuis BigQuery
def obtenir_dernier_filigrane(client_bq):
    requete = f"""
        SELECT dernier_succes
        FROM `{PROJET_ID}.entrepot_mobilite.filigrane_etat`
        WHERE identifiant_flux = @flux_id
        ORDER BY dernier_succes DESC
        LIMIT 1
    """
    config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("flux_id", "STRING", FLUX_ID)]
    )
    try:
        resultats = list(client_bq.query(requete, job_config=config))
        if resultats:
            return resultats[0].dernier_succes
    except Exception as err:
        print(f"Information : aucun filigrane preexistant trouve ({err})")
    return None


# Fonction de mise a jour du filigrane d execution
def actualiser_filigrane(client_bq, nouvel_horodatage):
    if not nouvel_horodatage:
        return
    requete = f"""
        MERGE `{PROJET_ID}.entrepot_mobilite.filigrane_etat` AS cible
        USING (SELECT @flux_id AS identifiant_flux, @dernier_succes AS dernier_succes) AS source
        ON cible.identifiant_flux = source.identifiant_flux
        WHEN MATCHED THEN
          UPDATE SET dernier_succes = source.dernier_succes, actualise_le = CURRENT_TIMESTAMP()
        WHEN NOT MATCHED THEN
          INSERT (identifiant_flux, dernier_succes, actualise_le)
          VALUES (source.identifiant_flux, source.dernier_succes, CURRENT_TIMESTAMP())
    """
    config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("flux_id", "STRING", FLUX_ID),
            bigquery.ScalarQueryParameter("dernier_succes", "TIMESTAMP", nouvel_horodatage)
        ]
    )
    try:
        client_bq.query(requete, job_config=config).result()
        print("Filigrane actualise avec succes dans BigQuery.")
    except Exception as err:
        print(f"Avertissement : actualisation du filigrane non effectuee ({err})")


# Fonction d extraction iterative par pagination par curseur offset
def extraire_stations_velib():
    stations_totales = []
    offset_courant = 0
    page_numero = 1

    while page_numero <= LIMITE_PAGES_MAX:
        parametres = {
            "limit": TAILLE_LOT,
            "offset": offset_courant,
            "order_by": "duedate DESC"
        }
        try:
            reponse = requests.get(API_URL, params=parametres, timeout=15)
            reponse.raise_for_status()
            donnees_json = reponse.json()
        except requests.exceptions.RequestException as erreur:
            print(f"Erreur d acces API page {page_numero} : {erreur}")
            break

        enregistrements_page = donnees_json.get("results", [])
        total_declare = donnees_json.get("total_count", 0)

        if not enregistrements_page:
            break

        stations_totales.extend(enregistrements_page)
        offset_courant += len(enregistrements_page)

        if offset_courant >= total_declare:
            break

        page_numero += 1
        time.sleep(0.1)

    return stations_totales


# Fonction pure de normalisation des attributs de mobilite
def transformer_mobilite(stations_brutes, dernier_filigrane=None):
    if not stations_brutes:
        return []

    horodatage_extraction = datetime.now(timezone.utc).isoformat()
    enregistrements = []

    for item in stations_brutes:
        date_mesure_str = item.get("duedate")
        if date_mesure_str:
            try:
                date_mesure = datetime.fromisoformat(date_mesure_str.replace("Z", "+00:00"))
            except ValueError:
                date_mesure = None
        else:
            date_mesure = None

        if dernier_filigrane and date_mesure and date_mesure <= dernier_filigrane:
            continue

        enregistrements.append({
            "station_id": str(item.get("stationcode") or ""),
            "nom_station": str(item.get("name") or ""),
            "commune": str(item.get("nom_arrondissement_communes") or ""),
            "capacite": item.get("capacity"),
            "velos_disponibles": item.get("numbikesavailable"),
            "bornes_libres": item.get("numdocksavailable"),
            "en_service": bool(item.get("is_installed") == "OUI" and item.get("is_renting") == "OUI"),
            "mesure_le": date_mesure_str,
            "date_ingestion_utc": horodatage_extraction
        })

    return enregistrements


# Fonction unitaire de controle de conformite metier
def valider_mobilite(ligne):
    if not ligne.get("station_id"):
        return None, "R01 station_id manquant"
    if ligne.get("velos_disponibles") is None or ligne["velos_disponibles"] < 0:
        return None, "R02 velos disponibles invalides"
    if ligne.get("bornes_libres") is None or ligne["bornes_libres"] < 0:
        return None, "R03 bornes libres invalides"
    if not ligne.get("mesure_le"):
        return None, "R04 date mesure absente"
    return ligne, None


# Fonction de conversion d une liste en format NDJSON
def formater_jsonl(enregistrements):
    return "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in enregistrements)


# Fonction d envoi d une chaine de caracteres vers Cloud Storage
def deposer_gcs(client, bucket_nom, chemin_cible, donnees_texte):
    bucket = client.bucket(bucket_nom)
    blob = bucket.blob(chemin_cible)
    blob.upload_from_string(donnees_texte, content_type="application/json")
    print(f"Fichier consigne avec succes gs://{bucket_nom}/{chemin_cible}")


# Fonction de depot determinant les chemins selon les zones
def charger_donnees(propres, rejets, date_lot):
    client = storage.Client()
    if propres:
        chemin_propres = f"{PREFIXE_STOCKAGE}/dt={date_lot}/data.jsonl"
        deposer_gcs(client, BUCKET_NOM, chemin_propres, formater_jsonl(propres))
    if rejets:
        chemin_rejets = f"{PREFIXE_STOCKAGE}_rejets/dt={date_lot}/data.jsonl"
        deposer_gcs(client, BUCKET_NOM, chemin_rejets, formater_jsonl(rejets))


# Fonction principale orchestrant le flux et les controles obligatoires
def executer_pipeline():
    date_lot = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    client_bq = None
    dernier_filigrane = None
    try:
        client_bq = bigquery.Client()
        dernier_filigrane = obtenir_dernier_filigrane(client_bq)
    except Exception as err:
        print(f"BigQuery non initialise en local ({err})")

    stations_brutes = extraire_stations_velib()
    volume_conforme, message_volume = controler_volume(len(stations_brutes))
    print(f"Controle volumetrique : {message_volume}")

    lignes_extraites = transformer_mobilite(stations_brutes, dernier_filigrane)

    enregistrements_propres = []
    enregistrements_rejetes = []
    plus_recent = None

    for ligne in lignes_extraites:
        valide, motif = valider_mobilite(ligne)
        if motif:
            enregistrements_rejetes.append({
                **ligne,
                "motif_rejet": motif,
                "rejete_le_utc": datetime.now(timezone.utc).isoformat()
            })
        else:
            enregistrements_propres.append(valide)
            date_str = valide.get("mesure_le")
            if date_str:
                try:
                    instant = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    if plus_recent is None or instant > plus_recent:
                        plus_recent = instant
                except ValueError:
                    pass

    if enregistrements_propres or enregistrements_rejetes:
        charger_donnees(enregistrements_propres, enregistrements_rejetes, date_lot)

    if client_bq and plus_recent:
        actualiser_filigrane(client_bq, plus_recent)

    bilan = {
        "date_lot": date_lot,
        "lues": len(lignes_extraites),
        "gardees": len(enregistrements_propres),
        "rejetees": len(enregistrements_rejetes),
        "stations_brutes": len(stations_brutes)
    }
    bilan["coherent"] = bilan["lues"] == (bilan["gardees"] + bilan["rejetees"])
    print(f"BILAN OPERATIONNEL {json.dumps(bilan)}")
    if not bilan["coherent"]:
        raise RuntimeError(f"Rupture de coherence dans le pipeline {bilan}")
    return bilan


# Point d entree HTTP pour l execution en Cloud Function
def point_entree_http(request):
    try:
        resultat = executer_pipeline()
        return (json.dumps(resultat), 200, {"Content-Type": "application/json"})
    except Exception as erreur:
        print(f"Defaillance d execution du pipeline {erreur}")
        return (json.dumps({"erreur": str(erreur)}), 500, {"Content-Type": "application/json"})


if __name__ == "__main__":
    executer_pipeline()
