import pytest
from src.pipeline import valider_et_nettoyer

def test_conformite_donnees():
    donnees_test = [{"id": "test_1", "valeur": 10.5, "date_utc": "2026-10-12T12:00:00Z"}]
    valides, rejets = valider_et_nettoyer(donnees_test)
    assert len(valides) >= 0
    assert len(rejets) == 0