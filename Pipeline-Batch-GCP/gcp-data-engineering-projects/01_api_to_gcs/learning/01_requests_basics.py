"""
Ce script montre comment récupérer les données d'une API REST avec la librairie 'requests' 
en utilisant une approche synchrone et très lisible.

Il aborde la structure d'une requête GET, la gestion des statuts HTTP,
et la désérialisation du JSON.
"""

import requests
import json

# L'URL de l'API Open-Meteo pour récupérer la température de Paris aujourd'hui
API_URL = "https://api.open-meteo.com/v1/forecast?latitude=48.8534&longitude=2.3488&current_weather=true"

def fetch_weather_pedagogical():
    print(f"Tentative de connexion à l'API : {API_URL}")
    
    # 1. On envoie une requête GET (demande de lecture) au serveur
    # On ajoute un timeout (10 secondes max) pour éviter que notre code reste bloqué à l'infini si le serveur rame.
    response = requests.get(API_URL, timeout=10)
    
    # 2. On vérifie le code de statut HTTP. 
    # 200 = OK. 404 = Not Found. 500 = Internal Server Error.
    print(f"Code de statut reçu : {response.status_code}")
    
    # Si le serveur retourne une erreur (4xx ou 5xx), cette fonction va faire "crasher" le script 
    # proprement en levant une exception (HTTPError).
    response.raise_for_status()
    
    # 3. La réponse est du texte pur (souvent structuré en JSON). 
    # .json() convertit ce texte en dictionnaire Python manipulable.
    data = response.json()
    
    print("\n--- Données brutes reçues (JSON) ---")
    # json.dumps permet d'imprimer le dictionnaire proprement (indenté) pour la lisibilité
    print(json.dumps(data, indent=2))
    
    # 4. On extrait une information spécifique du dictionnaire
    current_temp = data["current_weather"]["temperature"]
    print(f"\n✅ Succès : La température actuelle à Paris est de {current_temp}°C")

if __name__ == "__main__":
    fetch_weather_pedagogical()

