# -*- coding: utf-8 -*-
"""Point d'entree Cloud Run. Le meme pipeline, declenche par HTTP.

Trois differences avec le lancement local, et trois seulement.

  1. La fonction prend un parametre `request`, exige par le service.
  2. Elle rend un couple (corps, code HTTP). Un echec rend 500.
  3. La configuration vient des variables d'environnement, posees au
     deploiement.
"""

import json
import os

import requests
from google.cloud import storage

from pipeline import executer


def run_pipeline(request):
    """Declenche par Cloud Scheduler. Rend 200 ou 500, jamais autre chose."""
    try:
        bilan = executer(storage.Client(), requests.Session(),
                         os.environ["BUCKET"])
      except Exception as erreur:
        print(json.dumps({"severity": "ERROR", "statut": "ECHEC",
                          "jour": jour, "erreur": type(erreur).__name__,
                          "detail": str(erreur)[:500]}))
        return ("erreur", 500)

    print(json.dumps(bilan, ensure_ascii=False))
    return json.dumps(bilan, ensure_ascii=False), 200