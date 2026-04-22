# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Sauvegarde / Chargement
# ─────────────────────────────────────────────────────────────────────────────
#
#  À QUOI SERT CE FICHIER ?
#  ------------------------
#  Deux choses, dans DEUX FICHIERS différents :
#
#       save.json         — la SAUVEGARDE de la partie en cours (position du
#                           joueur, PV, scène active, etc.). Modifié quand
#                           le joueur sauvegarde, lu au "Continuer" du menu.
#
#       game_config.json  — la CONFIG persistante (résolution, volumes,
#                           options, nombre de compagnons par défaut...).
#                           Reste valable d'une partie à l'autre.
#
#  Pour les deux, on passe par JSON parce que c'est :
#       - lisible à l'œil (un humain peut éditer le fichier au notepad)
#       - sans dépendance (Python en a la lib en standard)
#       - sans danger (pas de pickle = pas de code arbitraire à l'ouverture)
#
#  EXEMPLE CONCRET
#  ---------------
#       # Le joueur sauvegarde sa partie :
#       save_system.sauvegarder({
#           "joueur":   {"x": 1200, "y": 450, "hp": 3},
#           "scene":    "foret_haute",
#           "horloge":  3.42,
#       })
#       → écrit save.json dans le dossier racine du jeu.
#
#       # Au démarrage suivant, "Continuer" :
#       data = save_system.charger()
#       if data is None:
#           print("Pas de sauvegarde.")     # 1ère fois ou fichier corrompu
#       else:
#           joueur.x = data["joueur"]["x"]
#           ...
#
#  Petit lexique :
#     - JSON         = "JavaScript Object Notation". Format texte universel
#                      pour écrire des dicts/listes/nombres/strings. Lit
#                      par tous les langages, et lisible à l'œil nu.
#     - sérialisation= "transformer un objet en texte/octets" (pour le
#                      sauvegarder / l'envoyer). json.dump = sérialise vers
#                      un fichier. json.load = désérialise depuis un fichier.
#     - encoding="utf-8" = on précise que le texte est en UTF-8 (= peut
#                      contenir des accents, caractères spéciaux, etc.).
#                      Sans ça, Windows utiliserait sa locale → incompatibilité
#                      entre machines.
#     - chemin absolu= un chemin qui démarre par C:\ (Windows) ou / (Linux).
#                      On en construit un avec os.path.join + __file__ pour
#                      être SÛRS de viser le bon dossier, peu importe d'où
#                      on lance le script.
#     - silent fail  = "échec silencieux" — on attrape l'exception et on
#                      renvoie None ou {} au lieu de crasher. Pertinent ici :
#                      si le fichier est absent ou corrompu, on préfère que
#                      le jeu démarre quand même (en partie neuve) plutôt
#                      qu'avec un écran d'erreur.
#
#  POURQUOI try / except Exception PARTOUT ?
#  -----------------------------------------
#  Beaucoup de raisons peuvent rendre un fichier illisible : disque plein,
#  permissions, JSON cassé manuellement, crash en cours d'écriture, etc.
#  Plutôt que d'énumérer chaque cas, on attrape Exception et on renvoie
#  une valeur sûre. Le jeu continue → l'utilisateur perd peut-être sa
#  sauvegarde, mais il peut au moins relancer une partie.
#
#  POURQUOI _BASE = os.path.dirname(os.path.dirname(__file__)) ?
#  -------------------------------------------------------------
#  __file__               → chemin de CE fichier (systems/save_system.py)
#  dirname(__file__)      → dossier parent → "systems/"
#  dirname(dirname(...))  → dossier grand-parent → racine ENTRE-DEUX/
#  Comme ça, save.json est rangé À LA RACINE du projet, peu importe où
#  l'utilisateur a lancé Python.
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  ui/menu.py     : "Continuer" appelle charger().
#  core/game.py   : sauvegarde automatique à certains moments → sauvegarder().
#  ui/settings_screen.py : lit/écrit la config via lire_config / ecrire_config.
#
#  JE VEUX MODIFIER QUOI ?
#  -----------------------
#     - Plusieurs SLOTS de sauvegarde       → ajouter un argument `slot` aux
#                                              fonctions et coller dans le nom
#                                              de fichier (save_1.json, ...).
#     - Sauvegarde COMPRESSÉE (gzip)        → wrapper gzip.open au lieu de open
#     - Garde-fou sur la version            → ajouter "version" dans data,
#                                              vérifier au chargement.
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D24]  module avec état partagé — _BASE/_CHEMIN/_CONFIG sont calculés
#                                       UNE seule fois à l'import.
#
# ─────────────────────────────────────────────────────────────────────────────

import json
import os


# ═════════════════════════════════════════════════════════════════════════════
#  CHEMINS (calculés une fois à l'import — voir explication dans le header)
# ═════════════════════════════════════════════════════════════════════════════

_BASE   = os.path.dirname(os.path.dirname(__file__))   # racine du projet
_CHEMIN = os.path.join(_BASE, "save.json")             # sauvegarde de partie
_CONFIG = os.path.join(_BASE, "game_config.json")      # config persistante


# ═════════════════════════════════════════════════════════════════════════════
#  1. SAUVEGARDE DE PARTIE (save.json)
# ═════════════════════════════════════════════════════════════════════════════

def sauvegarder(data):
    """Écrit `data` (un dict) dans save.json. Écrase l'ancien."""
    with open(_CHEMIN, "w", encoding="utf-8") as f:
        json.dump(data, f)


def charger():
    """Lit save.json et renvoie le dict. Renvoie None si pas de sauvegarde
    ou fichier corrompu (cf. silent fail dans le header)."""
    if not os.path.exists(_CHEMIN):
        return None
    try:
        with open(_CHEMIN, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def supprimer():
    """Efface la sauvegarde (ex : "Nouvelle partie" du menu)."""
    if os.path.exists(_CHEMIN):
        os.remove(_CHEMIN)


# ═════════════════════════════════════════════════════════════════════════════
#  2. CONFIG PERSISTANTE (game_config.json)
# ═════════════════════════════════════════════════════════════════════════════

def lire_config():
    """Renvoie la config (dict). Renvoie {} si pas de config ou corrompu."""
    if not os.path.exists(_CONFIG):
        return {}
    try:
        with open(_CONFIG, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def ecrire_config(data):
    """Écrit la config en INDENTÉ (lisible à l'œil nu, contrairement à
    save.json qu'on sauve compact). Échec silencieux si écriture impossible."""
    try:
        with open(_CONFIG, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass
