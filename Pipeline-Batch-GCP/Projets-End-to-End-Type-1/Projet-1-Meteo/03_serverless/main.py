# -*- coding: utf-8 -*-
"""Point d'entree Cloud Functions Gen 2 / Cloud Run."""

import json
import os
from datetime import datetime, timezone

import requests
from google.cloud import storage

from pipeline import executer


def run_pipeline(request):
    """Declenche par Cloud Scheduler en HTTP. Rend 200 en cas de succes, 500 en echec."""
    try:
        bucket = os.environ.get("BUCKET", f"data-lake-meteo-{os.environ.get('GCP_PROJECT', '')}")
        bilan = executer(storage.Client(), requests.Session(), bucket)
        print(json.dumps(bilan, ensure_ascii=False))
        return (json.dumps(bilan, ensure_ascii=False), 200, {"Content-Type": "application/json"})
    except Exception as erreur:
        print(json.dumps({
            "severity": "ERROR",
            "statut": "ECHEC",
            "date_utc": datetime.now(timezone.utc).isoformat(),
            "erreur": type(erreur).__name__,
            "detail": str(erreur)[:500]
        }))
        return (json.dumps({"erreur": str(erreur)}), 500, {"Content-Type": "application/json"})
