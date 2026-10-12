import pytest
from src.pipeline import nettoyer_donnees

def test_validation_crypto_conforme():
    donnees_brutes = [
        {"id": "bitcoin", "symbol": "btc", "current_price": 82875.0, "last_updated": "2026-10-12T12:00:00Z"},
        {"id": "ethereum", "symbol": "eth", "current_price": 2534.28, "last_updated": "2026-10-12T12:00:00Z"}
    ]
    valides, rejets = nettoyer_donnees(donnees_brutes)
    assert len(valides) == 2
    assert len(rejets) == 0
    assert valides[0]["actif"] == "bitcoin"
    assert valides[0]["prix_usd"] == 82875.0

def test_rejet_prix_negatif():
    donnees_corrompues = [
        {"id": "fakecoin", "symbol": "fk", "current_price": -10.0, "last_updated": "2026-10-12T12:00:00Z"}
    ]
    valides, rejets = nettoyer_donnees(donnees_corrompues)
    assert len(valides) == 0
    assert len(rejets) == 1
    assert "prix_negatif_ou_nul" in rejets[0]["motif_rejet"]
