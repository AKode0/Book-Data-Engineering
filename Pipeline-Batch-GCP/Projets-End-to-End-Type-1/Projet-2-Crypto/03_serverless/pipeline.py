# Importation du module standard json pour la manipulation des charges utiles
import json
# Importation du module os pour la recuperation des variables d environnement
import os
# Importation des utilitaires d horodatage pour generer des temps UTC stricts
from datetime import datetime, timezone

# Importation de requests pour l emission des requetes HTTP vers CoinGecko
import requests
# Importation du client officiel Google Cloud Secret Manager pour la cle d API
from google.cloud import secretmanager
# Importation du client officiel Google Cloud Storage pour le stockage objet
from google.cloud import storage

# Identifiant du projet Google Cloud courant
PROJET_ID = os.environ.get("GCP_PROJECT", "projet-id-par-defaut")
# Nom du compartiment de stockage cible
BUCKET_NOM = os.environ.get("BUCKET_CRYPTO", "data-lake-crypto-defaut")
# Identifiant de la ressource dans Secret Manager
NOM_SECRET = "cle-coingecko-api"
# URL de l API CoinGecko pour la cotation des actifs
API_URL = "https://api.coingecko.com/api/v3/simple/price"
# Parametres de requete ciblant Bitcoin et Ethereum libelles en dollar USD
PARAMS = {"ids": "bitcoin,ethereum", "vs_currencies": "usd"}
# Prefixe du dossier logique sur Cloud Storage
PREFIXE_STOCKAGE = "api_crypto"


# Fonction d acces et de dechiffrement de la cle d API
def recuperer_secret(nom_secret, version="latest"):
    # Instanciation du client officiel Secret Manager
    client = secretmanager.SecretManagerServiceClient()
    # Construction du chemin complet de la version de secret
    chemin = f"projects/{PROJET_ID}/secrets/{nom_secret}/versions/{version}"
    # Requete de dechiffrement et acces a la charge utile
    reponse = client.access_secret_version(request={"name": chemin})
    # Decodage du flux binaire en chaine de caracteres UTF-8
    return reponse.payload.data.decode("UTF-8")


# Fonction d extraction securisee verifiant les codes d etat HTTP
def extraire_cours_crypto(cle_api):
    # Definition des en-tetes HTTP avec jeton prive d authentification
    headers = {
        # En-tête officiel CoinGecko Demo API
        "x-cg-demo-api-key": cle_api,
        # Format de reponse souhaite
        "Accept": "application/json"
    }
    # Ouverture d un bloc surveille pour les pannes reseau
    try:
        # Requete HTTP GET avec temporisation maximale de dix secondes
        reponse = requests.get(API_URL, params=PARAMS, headers=headers, timeout=10)
        # Declenchement d une exception si le statut HTTP est anormal
        reponse.raise_for_status()
        # Conversion du corps de reponse en dictionnaire Python
        return reponse.json()
    # Capture explicite des reponses de statut HTTP d erreur
    except requests.exceptions.HTTPError as err:
        # Extraction du code numerique recu
        statut = err.response.status_code
        # Diagnostic du rejet d authentification
        if statut == 401:
            # Consigne d alerte sur la validite de la cle d acces
            print("Erreur 401 cle d API invalide ou en-tete mal nomme.")
        # Diagnostic du depassement de quota
        elif statut == 429:
            # Consigne d alerte sur le plafond de frequence
            print("Erreur 429 quota d appels depasse veuillez respecter Retry-After.")
        # Diagnostic des autres anomalies HTTP
        else:
            # Consigne d alerte sur le code generique
            print(f"Erreur HTTP {statut} renvoyee par le service.")
    # Capture de toute autre exception de transport
    except Exception as err:
        # Journalisation de l anomalie inattendue
        print(f"Erreur inattendue lors de l extraction {err}")
    # Renvoi explicite de None en cas d echec
    return None


# Fonction pure d aplatissement de la reponse en liste tabulaire
def transformer_crypto(brut):
    # Verification prealable de l existence de la reponse
    if not brut:
        # Restitution d une liste vide en l absence de donnees
        return []
    # Generation de l horodatage logique UTC de la collecte
    horodatage = datetime.now(timezone.utc).isoformat()
    # Initialisation de la collection des enregistrements
    enregistrements = []
    # Parcours des actifs et de leurs sous-dictionnaires
    for actif, valeurs in brut.items():
        # Adjonction d une ligne aplatie et standardisee
        enregistrements.append({
            # Identifiant de l actif financier
            "actif": actif,
            # Cours de cloture exprime en dollar USD
            "prix_usd": valeurs.get("usd"),
            # Horodatage logique de l extraction
            "date_ingestion_utc": horodatage
        })
    # Restitution des enregistrements formates
    return enregistrements


# Fonction unitaire de controle de conformite metier
def valider_crypto(ligne):
    # Verification de la presence physique du symbole de l actif
    if not ligne.get("actif"):
        # Rejet pour absence d identifiant d actif
        return None, "R01 actif financier absent"
    # Verification de la presence de la valorisation monetaire
    if ligne.get("prix_usd") is None:
        # Rejet pour absence de prix de marche
        return None, "R02 cours de valorisation absent"
    # Verification de la positivite stricte du prix
    if ligne["prix_usd"] <= 0:
        # Rejet pour valeur negative ou nulle
        return None, f"R03 cours negatif ou nul {ligne['prix_usd']}"
    # Confirmation de conformite de la ligne
    return ligne, None


# Fonction de conversion d une liste en format NDJSON
def formater_jsonl(enregistrements):
    # Serialisation ligne a ligne sans retours internes
    return "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in enregistrements)


# Fonction d envoi d une chaine de caracteres vers Cloud Storage
def deposer_gcs(client, bucket_nom, chemin_cible, donnees_texte):
    # Selection du compartiment distant
    bucket = client.bucket(bucket_nom)
    # Instanciation de l objet blob
    blob = bucket.blob(chemin_cible)
    # Depot du contenu texte sous encodage JSON
    blob.upload_from_string(donnees_texte, content_type="application/json")
    # Message de confirmation d ecriture
    print(f"Fichier consigne avec succes gs://{bucket_nom}/{chemin_cible}")


# Fonction de depot determinant les chemins selon les zones
def charger_donnees(propres, rejets, date_lot):
    # Instanciation du client Cloud Storage
    client = storage.Client()
    # Traitement des lignes conformes
    if propres:
        # Chemin deterministe en zone brute partitionnee
        chemin_propres = f"{PREFIXE_STOCKAGE}/dt={date_lot}/data.jsonl"
        # Envoi physique vers le stockage distant
        deposer_gcs(client, BUCKET_NOM, chemin_propres, formater_jsonl(propres))
    # Traitement des anomalies
    if rejets:
        # Chemin reserve au compartiment des rejets motives
        chemin_rejets = f"{PREFIXE_STOCKAGE}_rejets/dt={date_lot}/data.jsonl"
        # Envoi physique vers le stockage distant
        deposer_gcs(client, BUCKET_NOM, chemin_rejets, formater_jsonl(rejets))


# Fonction principale orchestrant le flux et les controles obligatoires
def executer_pipeline():
    # Calcul de la date logique du jour
    date_lot = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Recuperation securisee du secret depuis Secret Manager
    cle_api = recuperer_secret(NOM_SECRET)
    # Extraction des valorisations brutes
    donnees_brutes = extraire_cours_crypto(cle_api)
    # Transformation et aplatissement des structures
    lignes_extraites = transformer_crypto(donnees_brutes)

    # Initialisation de la collection des lignes saines
    enregistrements_propres = []
    # Initialisation de la collection des rejets
    enregistrements_rejetes = []

    # Iteration sur l ensemble des lignes collectees
    for ligne in lignes_extraites:
        # Soumission au filtre de validation
        valide, motif = valider_crypto(ligne)
        # Branchement en presence d anomalie
        if motif:
            # Enregistrement dans les rejets avec motif
            enregistrements_rejetes.append({
                # Donnee brute d origine
                **ligne,
                # Motif technique unique
                "motif_rejet": motif,
                # Horodatage de l operation
                "rejete_le_utc": datetime.now(timezone.utc).isoformat()
            })
        # Branchement si la donnee est saine
        else:
            # Enregistrement dans les lignes conformes
            enregistrements_propres.append(valide)

    # Transfert physique vers Cloud Storage
    charger_donnees(enregistrements_propres, enregistrements_rejetes, date_lot)

    # Construction du bilan d execution
    bilan = {
        # Date logique de reference
        "date_lot": date_lot,
        # Total de lignes en entree
        "lues": len(lignes_extraites),
        # Total de lignes admises
        "gardees": len(enregistrements_propres),
        # Total de lignes refusees
        "rejetees": len(enregistrements_rejetes),
        # Indicateur de bonne fin de la collecte
        "extraction_reussie": donnees_brutes is not None
    }
    # Verification de l assertion arithmetique non negociable
    bilan["coherent"] = bilan["lues"] == (bilan["gardees"] + bilan["rejetees"])

    # Impression du rapport d execution
    print(f"BILAN OPERATIONNEL {json.dumps(bilan)}")
    # Levee d alerte critique en cas de rupture arithmetique
    if not bilan["coherent"]:
        # Interruption du pipeline
        raise RuntimeError(f"Rupture de coherence dans le pipeline {bilan}")
    # Restitution du bilan
    return bilan


# Point d entree HTTP pour l execution en Cloud Function
def point_entree_http(request):
    # Bloc surveille pour capturer toute panne inattendue
    try:
        # Execution du traitement
        resultat = executer_pipeline()
        # Code HTTP 200 en cas de succes
        return (json.dumps(resultat), 200, {"Content-Type": "application/json"})
    # Capture des defaillances non resolues
    except Exception as erreur:
        # Journalisation systeme de l exception
        print(f"Defaillance d execution du pipeline {erreur}")
        # Code HTTP 500 obligatoire pour activer les reprises
        return (json.dumps({"erreur": str(erreur)}), 500, {"Content-Type": "application/json"})


# Bloc d execution directe en environnement local
if __name__ == "__main__":
    # Lancement local
    executer_pipeline()