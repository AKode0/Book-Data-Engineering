"""
Cours 04 : Interagir avec le Cloud Storage (Data Lake).

Ce script montre comment s'authentifier auprès de Google Cloud en utilisant
notre fichier JSON secret, puis comment créer un fichier virtuel et le pousser
dans notre Bucket (Data Lake).
"""

import json
# On importe la librairie officielle de Google pour le Storage
from google.cloud import storage
# On importe le module qui gère l'authentification
from google.oauth2 import service_account

# 1. PARAMÈTRES DE CONNEXION
# Le chemin vers ton fichier secret (qui est protégé par ton .gitignore !)
KEY_PATH = "/Users/fofanalazeny/Desktop/Book-Data-Engineering/gcp-data-engineering-projects/01_api_to_gcs/gcp-credentials.json"
# REMPLACE CETTE VALEUR par le nom unique de ton bucket
BUCKET_NAME = "data-lake-fofana-lazeny-2026" 

# -------------------------------------------------------------------------
# THEORIE : LE CLIENT CLOUD
# En Data Engineering, on ne communique jamais directement avec le Cloud.
# On instancie un "Client" (un objet Python) qui possède notre badge d'accès,
# et c'est à lui qu'on donne nos ordres (ex: client.upload_file()).
# -------------------------------------------------------------------------

def upload_to_gcs(data_dict, destination_blob_name):
    """
    Rôle : S'authentifier sur GCP et envoyer un dictionnaire Python 
    sous forme de fichier JSON dans le bucket.
    """
    
    print("1. Lecture du badge d'accès (Credentials)...")
    try:
        # On charge les credentials (le badge) depuis le fichier JSON
        credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
        
        # On instancie le Client GCS en lui donnant notre badge
        client = storage.Client(credentials=credentials)
    except Exception as e:
        print(f"❌ Erreur d'authentification (Vérifie ton fichier JSON) : {e}")
        return

    print(f"2. Connexion au bucket : {BUCKET_NAME}...")
    try:
        # On cible le bucket spécifique
        bucket = client.bucket(BUCKET_NAME)
        
        # On cible le "blob" (c'est le nom du fichier tel qu'il apparaîtra dans le cloud)
        blob = bucket.blob(destination_blob_name)
        
        # On transforme notre dictionnaire Python en texte JSON
        json_data_as_string = json.dumps(data_dict)
        
        print("3. Envoi de la donnée en cours...")
        # L'ordre d'upload final ! On précise le "content_type" pour que GCP sache que c'est du JSON
        blob.upload_from_string(json_data_as_string, content_type="application/json")
        
        print(f"✅ SUCCÈS ! Fichier uploadé sous le nom '{destination_blob_name}' dans le cloud.")
    except Exception as e:
        print(f"❌ Erreur lors de l'upload : {e}")

if __name__ == "__main__":
    # On crée une fausse donnée pour tester notre script d'upload indépendamment
    dummy_data = {
        "projet": "Data Engineering Portfolio",
        "etape": "Upload GCS",
        "statut": "Reussi"
    }
    
    # On choisit le nom du fichier qui sera créé dans le cloud
    # Note : On peut créer des "faux dossiers" en mettant des slashs !
    nom_du_fichier_cloud = "raw/test_upload_01.json"
    
    upload_to_gcs(dummy_data, nom_du_fichier_cloud)
