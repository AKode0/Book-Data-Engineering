import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.pipeline import valider_crypto, transformer_crypto

def test_validation_crypto_conforme():
    ligne = {
        "actif": "bitcoin",
        "prix_usd": 82875.0,
        "date_ingestion_utc": "2026-10-12T12:00:00Z"
    }
    valide, rejet = valider_crypto(ligne)
    assert valide is not None
    assert rejet is None
    assert valide["actif"] == "bitcoin"
    assert valide["prix_usd"] == 82875.0

def test_rejet_prix_negatif():
    ligne = {
        "actif": "fakecoin",
        "prix_usd": -10.0,
        "date_ingestion_utc": "2026-10-12T12:00:00Z"
    }
    valide, rejet = valider_crypto(ligne)
    assert valide is None
    assert "R03" in rejet

def test_rejet_actif_manquant():
    ligne = {
        "prix_usd": 100.0,
        "date_ingestion_utc": "2026-10-12T12:00:00Z"
    }
    valide, rejet = valider_crypto(ligne)
    assert valide is None
    assert "R01" in rejet

def test_transformation_crypto():
    brut = {
        "bitcoin": {"usd": 82875.0},
        "ethereum": {"usd": 2534.28}
    }
    lignes = transformer_crypto(brut)
    assert len(lignes) == 2
    assert lignes[0]["actif"] == "bitcoin"
    assert lignes[0]["prix_usd"] == 82875.0
