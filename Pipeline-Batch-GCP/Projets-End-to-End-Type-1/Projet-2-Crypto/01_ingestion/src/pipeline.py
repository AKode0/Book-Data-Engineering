# Importation du module standard json pour la manipulation des flux de donnees
import json
# Importation du module os pour l extraction des variables d environnement
import os
# Importation des utilitaires temporels pour fixer les horodatages stricts
from datetime import datetime, timezone

# Importation de requests pour l emission des requetes HTTP vers CoinGecko
import requests
# Importation du client officiel Google Cloud Secret Manager pour la cle d API
from google.cloud import secretmanager
# Importation du client officiel Google Cloud Storage pour le stockage objet
from google.cloud import storage

# Identifiant du projet Google Cloud courant
PROJET_ID = os.environ.get("GCP_PROJECT", "projet-id-par-defaut")
# Nom du compartiment de stockage Cloud Storage
BUCKET_NOM = os.environ.get("BUCKET_CRYPTO", f"data-lake-crypto-{PROJET_ID}")
# Identifiant de la ressource dans Secret Manager
NOM_SECRET = "cle-coingecko-api"
# URL de l API CoinGecko pour la cotation des actifs
API_URL = "https://api.coingecko.com/api/v3/simple/price"
# Parametres de requete ciblant les cours des trois cryptomonnaies majeures
PARAMS = {"ids": "bitcoin,ethereum,solana", "vs_currencies": "usd"}
# Prefixe du dossier logique de stockage dans le lac
PREFIXE_STOCKAGE = "api_crypto"


# Fonction d acces et de dechiffrement de la cle d API (Secret Manager avec repli env)
def recuperer_secret(nom_secret, version="latest"):
    # 1. Verification d une variable d environnement locale
    cle_locale = os.environ.get("COINGECKO_API_KEY")
    if cle_locale:
        return cle_locale

    # 2. Appel du service Google Secret Manager
    try:
        client = secretmanager.SecretManagerServiceClient()
        chemin = f"projects/{PROJET_ID}/secrets/{nom_secret}/versions/{version}"
        reponse = client.access_secret_version(request={"name": chemin})
        return reponse.payload.data.decode("UTF-8").strip()
    except Exception as err:
        print(f"Information : Secret Manager non joignable ({err}). Utilisation cle demo.")
        return "CG-demo-key-fallback"


# Fonction d extraction des valorisations avec gestion du debit
def extraire_cours_crypto(cle_api):
    # Definition des en-tetes conformes incluant le secret d authentification
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": cle_api,
    }
    # Bloc de surveillance reseau
    try:
        # Requete GET vers le fournisseur CoinGecko avec delai limite de dix secondes
        reponse = requests.get(API_URL, params=PARAMS, headers=headers, timeout=10)
        reponse.raise_for_status()
        return reponse.json()
    # Interception specifique des limitations de debit HTTP 429
    except requests.exceptions.HTTPError as erreur_http:
        statut = erreur_http.response.status_code
        if statut == 429:
            print("Quota depasse HTTP 429. Rejet temporaire applique.")
            return None
        elif statut in (401, 403):
            print(f"Erreur d authentification HTTP {statut}. Verification cle d API requise.")
            return None
        else:
            print(f"Anomalie HTTP non traitee {statut}.")
            return None
    # Interception des pannes physiques ou coupures reseau
    except requests.exceptions.RequestException as erreur_reseau:
        print(f"Defaillance de connectivite avec l API CoinGecko {erreur_reseau}")
        return None


# Fonction pure de transformation et d aplatissement des structures brutes
def transformer_crypto(brut):
    if not brut:
        return []
    horodatage = datetime.now(timezone.utc).isoformat()
    enregistrements = []
    for actif, valeurs in brut.items():
        enregistrements.append({
            "actif": actif,
            "prix_usd": valeurs.get("usd"),
            "date_ingestion_utc": horodatage
        })
    return enregistrements


# Fonction unitaire de controle de conformite metier
def valider_crypto(ligne):
    if not ligne.get("actif"):
        return None, "R01 actif financier absent"
    if ligne.get("prix_usd") is None:
        return None, "R02 cours de valorisation absent"
    if ligne["prix_usd"] <= 0:
        return None, f"R03 cours negatif ou nul {ligne['prix_usd']}"
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
    cle_api = recuperer_secret(NOM_SECRET)
    donnees_brutes = extraire_cours_crypto(cle_api)
    lignes_extraites = transformer_crypto(donnees_brutes)

    enregistrements_propres = []
    enregistrements_rejetes = []

    for ligne in lignes_extraites:
        valide, motif = valider_crypto(ligne)
        if motif:
            enregistrements_rejetes.append({
                **ligne,
                "motif_rejet": motif,
                "rejete_le_utc": datetime.now(timezone.utc).isoformat()
            })
        else:
            enregistrements_propres.append(valide)

    if enregistrements_propres or enregistrements_rejetes:
        charger_donnees(enregistrements_propres, enregistrements_rejetes, date_lot)

    bilan = {
        "date_lot": date_lot,
        "lues": len(lignes_extraites),
        "gardees": len(enregistrements_propres),
        "rejetees": len(enregistrements_rejetes),
        "extraction_reussie": donnees_brutes is not None
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
