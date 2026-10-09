"""
PIPELINE DE PRODUCTION : Open-Meteo vers Google Cloud Storage

Ce script est l'aboutissement de notre apprentissage. Il orchestre
les trois phases de notre pipeline d'ingestion (Extract, Transform, Load).
En entreprise, c'est ce fichier (et uniquement celui-là) qui sera exécuté 
tous les jours par un planificateur.
"""

import requests
import json
from datetime import datetime, timezone
from google.cloud import storage
from google.oauth2 import service_account

# --- CONFIGURATIONS ---
API_URL = "https://api.open-meteo.com/v1/forecast?latitude=48.8534&longitude=2.3488&current_weather=true"
KEY_PATH = "/Users/fofanalazeny/Desktop/Book-Data-Engineering/Pipeline-Batch-GCP/gcp-data-engineering-projects/01_api_to_gcs/gcp-credentials.json"  # Le chemin remonte de deux dossiers (src -> 01_api_to_gcs) pour trouver la clé
BUCKET_NAME = "data-lake-fofana-lazeny-2026"

# --- ETAPE 1 : EXTRACT ---
def extract_data(url):
    """Récupère les données de l'API de manière robuste."""
    print("🔄 [EXTRACT] Appel de l'API...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ [EXTRACT] Erreur fatale : {e}")
        return None

# --- ETAPE 2 : TRANSFORM (Parse) ---
def format_data(raw_data):
    """Ne garde que les champs utiles et ajoute le timestamp d'ingestion."""
    print("🔄 [TRANSFORM] Nettoyage de la donnée...")
    if not raw_data:
        return None
    
    current = raw_data.get("current_weather", {})
    return {
        "ville": "Paris", # On ajoute manuellement le contexte
        "latitude": raw_data.get("latitude"),
        "longitude": raw_data.get("longitude"),
        "temperature_celsius": current.get("temperature"),
        "windspeed_kmh": current.get("windspeed"),
        "ingestion_timestamp_utc": datetime.now(timezone.utc).isoformat()
    }

# --- ETAPE 3 : LOAD ---
def load_to_gcs(data, bucket_name, key_path):
    """Envoie la donnée propre dans le Data Lake."""
    print("🔄 [LOAD] Envoi vers Google Cloud Storage...")
    if not data:
        print("⚠️ [LOAD] Aucune donnée à envoyer. Annulation.")
        return
        
    try:
        credentials = service_account.Credentials.from_service_account_file(key_path)
        client = storage.Client(credentials=credentials)
        bucket = client.bucket(bucket_name)
        
        # On génère un nom de fichier unique basé sur l'heure exacte (très pratique pour ne pas écraser les anciens fichiers !)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_name = f"meteo_paris/weather_paris_{timestamp_str}.json"
        
        blob = bucket.blob(blob_name)
        blob.upload_from_string(json.dumps(data), content_type="application/json")
        print(f"✅ [LOAD] Succès ! Fichier sauvegardé : {blob_name}")
        
    except Exception as e:
        print(f"❌ [LOAD] Erreur d'envoi : {e}")

# --- ORCHESTRATION ---
def run_pipeline():
    """C'est le chef d'orchestre. Il appelle les fonctions dans le bon ordre."""
    print("🚀 DÉMARRAGE DU PIPELINE...")
    
    # 1. Extract
    raw_json = extract_data(API_URL)
    
    # 2. Transform
    clean_json = format_data(raw_json)
    
    # 3. Load
    load_to_gcs(clean_json, BUCKET_NAME, KEY_PATH)
    
    print("🏁 FIN DU PIPELINE.")

if __name__ == "__main__":
    run_pipeline()
