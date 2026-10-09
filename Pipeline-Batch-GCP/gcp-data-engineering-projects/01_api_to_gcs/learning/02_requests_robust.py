"""
Cours 02 : Rendre une requête HTTP robuste.

En production, une API externe est le maillon faible de ton architecture.
Ce script montre comment anticiper les erreurs (Exceptions) pour éviter
que ton pipeline de données ne s'arrête brutalement en plein milieu de la nuit.
"""

import requests
import json

API_URL = "https://api.open-meteo.com/v1/forecast?latitude=48.8534&longitude=2.3488&current_weather=true"

# On crée une fonction qui PREND UN PARAMÈTRE (url). 
# Cela rend notre boîte réutilisable pour n'importe quelle API !
def fetch_weather_robust(url):
    print(f"Tentative de connexion à : {url}")
    
    # Le bloc 'try' signifie "Essaie de faire ça, mais sois prêt à rattraper une erreur"
    try:
        response = requests.get(url, timeout=5)
        # Déclenche une erreur Python si le statut HTTP n'est pas 200 (OK)
        response.raise_for_status()
        
    # Le bloc 'except' capture l'erreur spécifique et permet d'agir au lieu de faire crasher le programme
    except requests.exceptions.Timeout:
        # Erreur très fréquente : le serveur n'a pas répondu dans les 5 secondes
        print("❌ ERREUR : L'API a mis trop de temps à répondre (Timeout).")
        return None
        
    except requests.exceptions.HTTPError as err:
        # Erreur côté serveur (ex: 404 Not Found, 500 Internal Error)
        print(f"❌ ERREUR HTTP : L'API a renvoyé une erreur : {err}")
        return None
        
    except requests.exceptions.RequestException as err:
        # Erreur réseau générale (ex: pas de connexion internet)
        print(f"❌ ERREUR RÉSEAU : Impossible de joindre l'API : {err}")
        return None

    # Si le bloc 'try' s'est bien passé, le code continue ici
    data = response.json()
    temp = data.get("current_weather", {}).get("temperature")
    
    print(f"✅ Succès : Température = {temp}°C")
    return temp

if __name__ == "__main__":
    # Test 1 : Avec une URL qui fonctionne
    print("--- Test 1 : API valide ---")
    fetch_weather_robust(API_URL)
    
    # Test 2 : Avec une fausse URL pour forcer et observer l'erreur HTTP (404)
    print("\n--- Test 2 : API qui n'existe pas ---")
    fake_url = "https://api.open-meteo.com/v1/fausse_page"
    fetch_weather_robust(fake_url)

