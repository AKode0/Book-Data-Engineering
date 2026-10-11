# -*- coding: utf-8 -*-
"""Pipeline meteo. Cinq villes, de l'API vers le data lake.

Trois fonctions pures et une qui depose. Les quatre controles du projet
sont portes ici.

  idempotence   le chemin de depot est cale sur le jour logique
  rejets        une ligne refusee part dans la zone de rejets, avec son
                motif, un seul, le premier qui bloque
  coherence     le bilan verifie lues == gardees + rejetees
  incremental   gere par la partition dt= cote entrepot
"""

import json
import os
from datetime import datetime, timezone

import requests

API_URL = os.environ.get("API_URL",
                         "https://api.open-meteo.com/v1/forecast")
BUCKET = os.environ.get("BUCKET", "data-lake-fofana-lazeny-2026")
SUJET = "meteo"

VILLES = [
    {"ville": "Paris",     "latitude": 48.8534, "longitude": 2.3488},
    {"ville": "Lyon",      "latitude": 45.7640, "longitude": 4.8357},
    {"ville": "Marseille", "latitude": 43.2965, "longitude": 5.3698},
    {"ville": "Nantes",    "latitude": 47.2184, "longitude": -1.5536},
    {"ville": "Abidjan",   "latitude": 5.3600,  "longitude": -4.0083},
]

TEMP_MIN, TEMP_MAX = -80.0, 60.0


def maintenant_utc() -> datetime:
    """Un seul endroit donne l'heure, et elle est en UTC."""
    return datetime.now(timezone.utc)


def jour_logique() -> str:
    """La date du lot. C'est elle qui nomme la partition."""
    return maintenant_utc().strftime("%Y-%m-%d")


def extraire(session, ville: dict) -> tuple[dict | None, str | None]:
    """Appelle l'API pour une ville. Rend (corps, motif_echec)."""
    try:
        r = session.get(API_URL, timeout=10, params={
            "latitude": ville["latitude"],
            "longitude": ville["longitude"],
            "current_weather": "true",
        })
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.Timeout:
        return None, "timeout api"
    except requests.exceptions.HTTPError as err:
        return None, f"http {err.response.status_code}"
    except requests.exceptions.RequestException as err:
        return None, f"reseau {type(err).__name__}"
    except ValueError:
        return None, "corps non json"


def transformer(brut: dict, ville: str, charge_le: str) -> dict:
    """Aplatit la reponse. Aucune validation ici, aucun appel reseau."""
    mesure = brut.get("current_weather") or {}
    return {
        "ville": ville,
        "latitude": brut.get("latitude"),
        "longitude": brut.get("longitude"),
        "temperature": mesure.get("temperature"),
        "vent_kmh": mesure.get("windspeed"),
        "releve_le": mesure.get("time"),
        # L'API rend l'heure SANS fuseau. Le fuseau est dans un champ a
        # part, et il faut le garder, sinon l'entrepot ne peut pas
        # savoir ce que l'heure veut dire.
        "fuseau": brut.get("timezone"),
        "charge_le": charge_le,
    }


def valider(ligne: dict) -> tuple[bool, str | None]:
    """Un seul motif par ligne, le premier qui bloque."""
    if ligne.get("temperature") is None:
        return False, "temperature absente"
    if not TEMP_MIN <= ligne["temperature"] <= TEMP_MAX:
        return False, "temperature hors bornes"
    if ligne.get("vent_kmh") is None:
        return False, "vent absent"
    if ligne.get("releve_le") is None:
        return False, "horodatage absent"
    return True, None


def rejet(ville: str, motif: str, ligne: dict | None,
          charge_le: str) -> dict:
    """Une ligne de rejet, toujours la MEME forme, quatre colonnes.

    La ligne d'origine part en TEXTE dans `brut`, pas en objet imbrique.
    Sinon la zone de rejets a un schema different d'un jour a l'autre et
    la detection automatique de BigQuery s'y perd.
    """
    return {"ville": ville, "motif": motif, "charge_le": charge_le,
            "brut": json.dumps(ligne, ensure_ascii=False) if ligne else None}


def en_jsonl(lignes: list[dict]) -> str:
    """Un objet JSON par ligne. Ce que BigQuery exige."""
    return "".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lignes)


def deposer(client, bucket_nom: str, chemin: str, contenu: str) -> None:
    """Un seul endroit ecrit sur le lake."""
    client.bucket(bucket_nom).blob(chemin).upload_from_string(
        contenu, content_type="application/x-ndjson")


def executer(client, session, bucket_nom: str = BUCKET) -> dict:
    """Le chef d'orchestre. Rend le bilan."""
    jour = jour_logique()
    charge_le = maintenant_utc().isoformat()

    gardees: list[dict] = []
    rejetees: list[dict] = []

    for ville in VILLES:
        brut, motif = extraire(session, ville)
        if motif:
            rejetees.append(rejet(ville["ville"], motif, None, charge_le))
            continue
        ligne = transformer(brut, ville["ville"], charge_le)
        ok, motif = valider(ligne)
        if ok:
            gardees.append(ligne)
        else:
            rejetees.append(rejet(ville["ville"], motif, ligne, charge_le))

      # Les DEUX zones recoivent un fichier a chaque passage, meme vide.
    # Un fichier vide dit « le pipeline a tourne et n'a rien rejete ».
    # Pas de fichier ne dit rien du tout, et c'est ambigu.
    deposer(client, bucket_nom,
            f"raw/{SUJET}/dt={jour}/mesures.jsonl", en_jsonl(gardees))
    deposer(client, bucket_nom,
            f"rejets/{SUJET}/dt={jour}/rejets.jsonl", en_jsonl(rejetees))

    bilan = {
        "jour": jour,
        "lues": len(VILLES),
        "gardees": len(gardees),
        "rejetees": len(rejetees),
    }
    bilan["coherent"] = bilan["lues"] == bilan["gardees"] + bilan["rejetees"]
    if not bilan["coherent"]:
        raise RuntimeError(f"bilan incoherent — {bilan}")
    return bilan


def main() -> dict:
    from google.cloud import storage
    bilan = executer(storage.Client(), requests.Session())
    print(json.dumps(bilan, ensure_ascii=False))
    return bilan


if __name__ == "__main__":
    main()