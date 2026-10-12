# -*- coding: utf-8 -*-
"""Les tests du pipeline meteo. Aucun reseau, aucun cloud."""

import json
import sys
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pipeline import VILLES, en_jsonl, executer, transformer, valider


# ---------------------------------------------------------------------
#   LES FAUX SERVICES. Memes noms de methodes que les vrais.
# ---------------------------------------------------------------------
class FauxBlob:
    def __init__(self, bucket, nom):
        self.bucket, self.name = bucket, nom

    def upload_from_string(self, contenu, content_type=None):
        deja = self.name in self.bucket.objets
        self.bucket.objets[self.name] = contenu
        self.bucket.depots += 1
        if deja:
            self.bucket.ecrasements += 1


class FauxBucket:
    def __init__(self, nom):
        self.name = nom
        self.objets, self.depots, self.ecrasements = {}, 0, 0

    def blob(self, nom):
        return FauxBlob(self, nom)


class FauxGCS:
    def __init__(self):
        self.buckets = {}

    def bucket(self, nom):
        return self.buckets.setdefault(nom, FauxBucket(nom))


class FausseReponse:
    def __init__(self, status_code=200, corps=None, texte=None):
        self.status_code, self._corps = status_code, corps
        self.text = texte if texte is not None else json.dumps(corps)

    def raise_for_status(self):
        if self.status_code >= 400:
            err = requests.exceptions.HTTPError(f"{self.status_code}")
            err.response = self
            raise err

    def json(self):
        if self._corps is None:
            raise ValueError("Expecting value: line 1 column 1 (char 0)")
        return self._corps


def mesure(temp, vent=11.0, heure="2026-10-11T08:00"):
    return {"latitude": 48.85, "longitude": 2.35, "timezone": "GMT",
            "current_weather": {"temperature": temp, "windspeed": vent,
                                "time": heure}}


class FausseAPI:
    """Une reponse par ville. Deux propres, trois abimees differemment."""

    PAR_VILLE = {
        "Paris":     FausseReponse(corps=mesure(14.2)),
        "Lyon":      FausseReponse(corps=mesure(16.8, 7.0)),
        "Marseille": FausseReponse(corps=mesure(999.0, 21.0)),
        "Nantes":    FausseReponse(corps={"latitude": 47.2,
                                          "longitude": -1.55}),
        "Abidjan":   FausseReponse(status_code=500, corps=None,
                                   texte="<html>Internal Error</html>"),
    }

    def __init__(self):
        self.appels = 0

    def get(self, url=None, params=None, timeout=None):
        self.appels += 1
        lat = params["latitude"]
        for v in VILLES:
            if v["latitude"] == lat:
                return self.PAR_VILLE[v["ville"]]
        return FausseReponse(status_code=404, corps=None, texte="not found")


# ---------------------------------------------------------------------
#   LA VALIDATION — un test par motif
# ---------------------------------------------------------------------
@pytest.mark.parametrize("ligne, attendu", [
    ({"temperature": 14.2, "vent_kmh": 11.0, "releve_le": "x"}, None),
    ({"temperature": None, "vent_kmh": 11.0, "releve_le": "x"},
     "temperature absente"),
    ({"temperature": 999.0, "vent_kmh": 11.0, "releve_le": "x"},
     "temperature hors bornes"),
    ({"temperature": 14.2, "vent_kmh": None, "releve_le": "x"},
     "vent absent"),
    ({"temperature": 14.2, "vent_kmh": 11.0, "releve_le": None},
     "horodatage absent"),
])
def test_valider_rend_un_seul_motif(ligne, attendu):
    ok, motif = valider(ligne)
    assert motif == attendu
    assert ok is (attendu is None)


def test_transformer_ne_plante_pas_sur_cle_absente():
    ligne = transformer({"latitude": 1.0}, "Paris", "2026-10-11T00:00:00Z")
    assert ligne["temperature"] is None
    assert ligne["ville"] == "Paris"
    assert ligne["fuseau"] is None


def test_transformer_garde_le_fuseau():
    ligne = transformer(mesure(14.2), "Paris", "2026-10-11T00:00:00Z")
    assert ligne["fuseau"] == "GMT"


def test_jsonl_une_ligne_par_objet():
    texte = en_jsonl([{"a": 1}, {"a": 2}])
    assert texte.count("\n") == 2
    assert "\n  " not in texte          # aucune indentation


# ---------------------------------------------------------------------
#   LE BILAN ET LA COHERENCE
# ---------------------------------------------------------------------
def test_bilan_coherent_et_complet():
    bilan = executer(FauxGCS(), FausseAPI(), "b")
    assert bilan["lues"] == 5
    assert bilan["gardees"] == 2          # Paris et Lyon
    assert bilan["rejetees"] == 3         # aberrante, sans mesure, 500
    assert bilan["coherent"] is True


def test_les_trois_motifs_de_rejet_sont_distincts():
    client = FauxGCS()
    executer(client, FausseAPI(), "b")
    chemin = [c for c in client.bucket("b").objets if c.startswith("rejets/")]
    assert len(chemin) == 1
    motifs = [json.loads(l)["motif"]
              for l in client.bucket("b").objets[chemin[0]].splitlines()]
    # Nantes n'a pas de bloc de mesure, donc la temperature est absente.
    # C'est le PREMIER motif qui bloque, pas l'horodatage.
    assert sorted(motifs) == ["http 500", "temperature absente",
                              "temperature hors bornes"]


# ---------------------------------------------------------------------
#   L'IDEMPOTENCE — elle se compte, elle ne se relit pas
# ---------------------------------------------------------------------
def test_deux_executions_laissent_un_seul_objet_par_zone():
    client = FauxGCS()
    executer(client, FausseAPI(), "b")
    executer(client, FausseAPI(), "b")

    bucket = client.bucket("b")
    assert bucket.depots == 4           # 2 zones x 2 executions
    assert len(bucket.objets) == 2      # une brute, une rejets
    assert bucket.ecrasements == 2      # la seconde a ecrase la premiere


def test_le_chemin_porte_le_jour_et_pas_l_heure():
    client = FauxGCS()
    executer(client, FausseAPI(), "b")
    chemins = list(client.bucket("b").objets)
    assert all("dt=" in c for c in chemins)
    assert all(c.endswith(".jsonl") for c in chemins)
    # Aucun chemin ne porte d'heure, de minute ni de seconde.
    assert not any(any(part.count("_") for part in c.split("/")[-1:])
                   for c in chemins)