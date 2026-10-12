import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.pipeline import valider_catalogue, transformer_catalogue

def test_validation_catalogue_conforme():
    ligne = {
        "identifiant": 1,
        "nom": "Rick Sanchez",
        "statut": "Alive",
        "date_ingestion_utc": "2026-10-12T12:00:00Z"
    }
    valide, rejet = valider_catalogue(ligne)
    assert valide is not None
    assert rejet is None
    assert valide["nom"] == "Rick Sanchez"

def test_rejet_identifiant_manquant():
    ligne = {"nom": "Sans ID", "date_ingestion_utc": "2026-10-12T12:00:00Z"}
    valide, rejet = valider_catalogue(ligne)
    assert valide is None
    assert "R01" in rejet

def test_transformation_catalogue():
    bruts = [{"id": 10, "name": "Morty", "status": "Alive", "species": "Human", "gender": "Male"}]
    transformes = transformer_catalogue(bruts)
    assert len(transformes) == 1
    assert transformes[0]["identifiant"] == 10
    assert transformes[0]["nom"] == "Morty"
