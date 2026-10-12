# -*- coding: utf-8 -*-
"""Audit d'une source. A relancer a chaque nouvelle API."""

import json
import requests

URL = "https://api.open-meteo.com/v1/forecast"
PARAMS = {"latitude": 48.8534, "longitude": 2.3488, "current_weather": "true"}


def auditer(url, params):
    r = requests.get(url, timeout=10, params=params)
    print("code      ", r.status_code)
    print("type       ", r.headers.get("Content-Type"))
    print("taille     ", len(r.content), "octets")
    r.raise_for_status()
    corps = r.json()

    print("racine     ", type(corps).__name__)
    print("cles       ", list(corps))
    for cle, valeur in corps.items():
        if isinstance(valeur, dict):
            print(f"  {cle} est un objet, cles {list(valeur)}")
        elif isinstance(valeur, list):
            print(f"  {cle} est un tableau de {len(valeur)} elements")

    print("\nextrait")
    print(json.dumps(corps, indent=2, ensure_ascii=False)[:600])
    return corps


if __name__ == "__main__":
    auditer(URL, PARAMS)