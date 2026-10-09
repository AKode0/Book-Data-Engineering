import requests
import json
from datetime import datetime, timezone
from google.cloud import storage
API_URL = "https://api.open-meteo.com/v1/forecast?latitude=48.8534&longitude=2.3488&current_weather=true"
BUCKET_NAME = "data-lake-fofana-lazeny-2026"
# Le "request" entre parenthèses est obligatoire pour Cloud Functions
def run_pipeline(request):
    print("🚀 DÉMARRAGE DU PIPELINE SUR CLOUD FUNCTIONS...")
    
    # 1. EXTRACT
    raw_data = requests.get(API_URL).json()
    
    # 2. TRANSFORM
    current = raw_data.get("current_weather", {})
    clean_json = {
        "ville": "Paris",
        "latitude": raw_data.get("latitude"),
        "longitude": raw_data.get("longitude"),
        "temperature_celsius": current.get("temperature"),
        "windspeed_kmh": current.get("windspeed"),
        "ingestion_timestamp_utc": datetime.now(timezone.utc).isoformat()
    }
    
    # 3. LOAD (Regarde : plus besoin de credentials.json !)
    client = storage.Client() 
    bucket = client.bucket(BUCKET_NAME)
    
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    blob_name = f"meteo_paris/weather_paris_{timestamp_str}.json"
    
    blob = bucket.blob(blob_name)
    blob.upload_from_string(json.dumps(clean_json), content_type="application/json")
    
    return f"✅ Succès ! Fichier {blob_name} sauvegardé dans GCS."