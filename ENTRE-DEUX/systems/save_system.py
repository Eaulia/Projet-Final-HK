# ─────────────────────────────────────────
#  ENTRE-DEUX — Sauvegarde / Chargement
# ─────────────────────────────────────────

import json
import os

_BASE    = os.path.dirname(os.path.dirname(__file__))
_CHEMIN  = os.path.join(_BASE, "save.json")
_CONFIG  = os.path.join(_BASE, "game_config.json")


def sauvegarder(data):
    with open(_CHEMIN, "w", encoding="utf-8") as f:
        json.dump(data, f)


def charger():
    if not os.path.exists(_CHEMIN):
        return None
    try:
        with open(_CHEMIN, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def supprimer():
    if os.path.exists(_CHEMIN):
        os.remove(_CHEMIN)


def lire_config():
    if not os.path.exists(_CONFIG):
        return {}
    try:
        with open(_CONFIG, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def ecrire_config(data):
    try:
        with open(_CONFIG, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass
