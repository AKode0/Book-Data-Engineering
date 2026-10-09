"""
Cours 03 : Extraction et Formatage de la donnée (Data Parsing).

Ce script montre comment prendre un gros bloc de données "brutes" (Raw)
renvoyé par une API, pour le transformer en un format propre, plat et standardisé
prêt à être envoyé dans notre Data Lake (Cloud).
"""

import requests
import json
# La librairie 'datetime' est un classique absolu en Data Engineering.
# Elle permet de manipuler les dates et les heures.
from datetime import datetime, timezone

API_URL = "https://api.open-meteo.com/v1/forecast?latitude=48.8534&longitude=2.3488&current_weather=true"

# -------------------------------------------------------------------------
# THEORIE : STRUCTURE D'UNE FONCTION DE TRANSFORMATION
# Une fonction (def) prend une "Entrée" (input), fait une opération, 
# et retourne une "Sortie" (output). 
# En Data Engineering, on sépare toujours l'extraction (parler à l'API) 
# de la transformation (modifier la donnée).
# -------------------------------------------------------------------------

def extract_raw_data(url):
    """
    Rôle : Contacter l'API et récupérer le JSON brut.
    Où on le retrouve en entreprise : C'est la toute première brique de ton pipeline (Extract).
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json() # Retourne le gros dictionnaire Python
    except Exception as e:
        print(f"Erreur d'extraction : {e}")
        return None


def format_weather_data(raw_json):
    """
    Rôle : Prendre le JSON brut, extraire les champs utiles, et ajouter 
    des métadonnées métiers (comme le timestamp d'ingestion).
    
    Où on le retrouve : C'est une étape de "Parsing" ou "Silver layer" légère.
    """
    
    # 1. On vérifie que le JSON reçu n'est pas vide
    if not raw_json:
        return None
    
    # 2. L'API Open-Meteo stocke les infos intéressantes sous la clé "current_weather".
    # La méthode .get() est vitale en Python. Si la clé "current_weather" n'existe pas
    # dans le JSON (API modifiée par surprise), .get() renverra un dictionnaire vide {} 
    # au lieu de faire crasher brutalement tout le code.
    current = raw_json.get("current_weather", {})
    
    # 3. Création du "Payload" (le paquet de données final qu'on va sauvegarder)
    # On reconstruit un dictionnaire plat, beaucoup plus facile à lire pour une base de données.
    formatted_data = {
        # On extrait la latitude et longitude du JSON brut
        "latitude": raw_json.get("latitude"),
        "longitude": raw_json.get("longitude"),
        
        # On extrait la température et la vitesse du vent du sous-dictionnaire
        "temperature_celsius": current.get("temperature"),
        "windspeed_kmh": current.get("windspeed"),
        
        # 4. LE TIMESTAMP D'INGESTION (Pratique critique en DE)
        # On ajoute toujours l'heure exacte à laquelle NOTRE pipeline a traité la donnée.
        # datetime.now(timezone.utc) donne l'heure universelle. 
        # .isoformat() transforme cette date en chaîne de caractères texte standardisée.
        "ingestion_timestamp_utc": datetime.now(timezone.utc).isoformat()
    }
    
    return formatted_data


if __name__ == "__main__":
    print("1. Lancement de l'extraction (Extract)...")
    raw_data = extract_raw_data(API_URL)
    
    print("\n2. Formatage de la donnée (Transform léger)...")
    clean_data = format_weather_data(raw_data)
    
    print("\n3. Résultat prêt pour le Data Lake :")
    # On imprime le résultat final. C'est CE bloc exact qui partira dans le Cloud.
    print(json.dumps(clean_data, indent=2))

