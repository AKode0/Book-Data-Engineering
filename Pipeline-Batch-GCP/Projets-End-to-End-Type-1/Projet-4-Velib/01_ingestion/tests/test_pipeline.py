import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.pipeline import valider_mobilite, transformer_mobilite, controler_volume

def test_validation_mobilite_conforme():
    ligne = {
        "station_id": "16107",
        "nom_station": "Benjamin Godard - Victor Hugo",
        "commune": "Paris",
        "capacite": 35,
        "velos_disponibles": 12,
        "bornes_libres": 23,
        "en_service": True,
        "mesure_le": "2026-10-12T12:00:00+00:00",
        "date_ingestion_utc": "2026-10-12T12:05:00+00:00"
    }
    valide, motif = valider_mobilite(ligne)
    assert valide is not None
    assert motif is None
    assert valide["station_id"] == "16107"
    assert valide["velos_disponibles"] == 12

def test_rejet_station_id_manquant():
    ligne = {
        "station_id": "",
        "velos_disponibles": 5,
        "bornes_libres": 10,
        "mesure_le": "2026-10-12T12:00:00+00:00"
    }
    valide, motif = valider_mobilite(ligne)
    assert valide is None
    assert "R01" in motif

def test_rejet_velos_negatifs():
    ligne = {
        "station_id": "16107",
        "velos_disponibles": -2,
        "bornes_libres": 10,
        "mesure_le": "2026-10-12T12:00:00+00:00"
    }
    valide, motif = valider_mobilite(ligne)
    assert valide is None
    assert "R02" in motif

def test_rejet_date_mesure_absente():
    ligne = {
        "station_id": "16107",
        "velos_disponibles": 5,
        "bornes_libres": 10,
        "mesure_le": None
    }
    valide, motif = valider_mobilite(ligne)
    assert valide is None
    assert "R04" in motif

def test_transformation_mobilite():
    brut = [{
        "stationcode": "16107",
        "name": "Benjamin Godard",
        "nom_arrondissement_communes": "Paris",
        "capacity": 35,
        "numbikesavailable": 10,
        "numdocksavailable": 25,
        "is_installed": "OUI",
        "is_renting": "OUI",
        "duedate": "2026-10-12T12:00:00Z"
    }]
    lignes = transformer_mobilite(brut)
    assert len(lignes) == 1
    assert lignes[0]["station_id"] == "16107"
    assert lignes[0]["bornes_libres"] == 25
    assert lignes[0]["en_service"] is True

def test_controle_volume():
    ok_normal, _ = controler_volume(1400)
    assert ok_normal is True

    trop_faible, msg_bas = controler_volume(500)
    assert trop_faible is False
    assert "reduit" in msg_bas
