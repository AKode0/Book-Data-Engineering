import functions_framework
from pipeline import executer_pipeline

@functions_framework.http
def point_entree_http(request):
    """Point d'entrée Cloud Function Gen 2 déclenché par Cloud Scheduler."""
    try:
        nb_enregistrements = executer_pipeline()
        return (f"Succès : {nb_enregistrements} cryptomonnaies ingérées.", 200)
    except Exception as e:
        return (f"Erreur d'ingestion : {str(e)}", 500)
