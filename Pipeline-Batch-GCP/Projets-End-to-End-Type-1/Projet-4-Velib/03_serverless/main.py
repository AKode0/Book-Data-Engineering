import functions_framework
import json
from pipeline import executer_pipeline

@functions_framework.http
def point_entree_http(request):
    """Point d'entrée Cloud Function Gen 2 déclenché par Cloud Scheduler."""
    try:
        resultat = executer_pipeline()
        return (json.dumps(resultat), 200, {"Content-Type": "application/json"})
    except Exception as erreur:
        print(f"Défaillance d'exécution du pipeline {erreur}")
        return (json.dumps({"erreur": str(erreur)}), 500, {"Content-Type": "application/json"})
