# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Configuration des hitboxes (par sprite)
# ─────────────────────────────────────────────────────────────────────────────
#
#  À QUOI SERT CE FICHIER ?
#  ------------------------
#  Le sprite du joueur fait, disons, 90×104 px (image visible). Mais sa
#  HITBOX (le rectangle invisible qui sert aux collisions) ne doit PAS faire
#  90×104 : sinon on est bloqué dès qu'un cheveu effleure une plateforme.
#  En pratique, on veut une hitbox plus petite, centrée sur le corps.
#
#  Chaque sprite (joueur + ennemis) a donc ses 4 valeurs :
#       w, h    = dimensions du rectangle de collision
#       ox, oy  = décalage du coin haut-gauche par rapport au sprite
#
#  Tout ça est stocké dans hitboxes.json, MODIFIABLE VISUELLEMENT depuis
#  l'éditeur (touche 6). Pas besoin d'éditer le code pour ajuster.
#
#  EXEMPLE CONCRET (un slime)
#  --------------------------
#       sprite slime.png : 64×48 px (image affichée)
#       hitbox configurée :
#           w=40, h=30   → rectangle 40×30 (plus petit que le sprite)
#           ox=12, oy=18 → ce rectangle commence 12 px à droite et
#                          18 px sous le coin haut-gauche du sprite
#
#       Résultat à l'écran :
#               sprite (64×48)
#               ┌──────────────┐
#               │   ┌──────┐   │   ← hitbox (40×30, décalée)
#               │   │      │   │
#               │   └──────┘   │
#               └──────────────┘
#
#  Petit lexique :
#     - hitbox     = rectangle invisible utilisé pour les collisions.
#                    Préférable plus PETIT que le sprite : ça pardonne
#                    les "coups dans le vide" → meilleur ressenti.
#     - sprite     = l'image affichée (souvent un .png).
#     - JSON       = format texte universel pour stocker dicts/listes
#                    (cf. systems/save_system.py pour le détail).
#     - cache      = on garde le contenu du JSON en mémoire après la
#                    1re lecture. Évite de relire le fichier à chaque
#                    appel de get_hitbox() (60 fois par seconde).
#     - clé spéciale __player__ : nom RÉSERVÉ utilisé pour le joueur.
#                    Pourquoi pas le nom de son sprite ? Parce que le
#                    joueur a PLUSIEURS frames (idle, marche, saut...) —
#                    la hitbox doit rester la même peu importe la frame.
#     - global     = mot-clé Python pour DIRE qu'on assigne à une variable
#                    de niveau module depuis une fonction (sinon Python
#                    crée une variable LOCALE). Cf. _load() / set_hitbox().
#
#  POURQUOI UN CACHE ?
#  -------------------
#  get_hitbox() est appelée à chaque création d'ennemi. Si on relisait
#  hitboxes.json à chaque appel, ça ferait beaucoup d'I/O disque pour
#  rien. Le cache (`_cache`) garde le contenu en mémoire. Premier appel :
#  on lit le fichier. Appels suivants : on renvoie ce qu'on a déjà.
#
#  POURQUOI DEFAULT_HITBOX vs DEFAULT_PLAYER_HITBOX ?
#  --------------------------------------------------
#  Le joueur a une taille particulière (haut et fin) → il a sa propre
#  valeur de repli. Les ennemis sont en moyenne plus carrés → 36×40
#  est un défaut plus raisonnable pour eux.
#
#  POURQUOI .copy() DANS LES VALEURS DE REPLI ?
#  --------------------------------------------
#  DEFAULT_HITBOX est un dict GLOBAL. Si get_hitbox() le renvoyait
#  directement et que l'appelant le modifiait, ça polluerait la valeur
#  par défaut pour TOUT LE MONDE. .copy() crée un dict indépendant.
#  Petit réflexe Python qui évite des bugs sourds.
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  entities/player.py : get_player_hitbox() au constructeur.
#  entities/enemy.py  : get_hitbox(sprite_name) pour chaque ennemi.
#  world/editor.py    : set_hitbox() / set_player_hitbox() depuis l'éditeur.
#
#  JE VEUX MODIFIER QUOI ?
#  -----------------------
#     - Hitboxes par défaut         → DEFAULT_HITBOX / DEFAULT_PLAYER_HITBOX
#     - Emplacement du fichier      → HITBOX_FILE
#     - Format de stockage (YAML?)  → adapter _load() et set_hitbox()
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D24]  module avec état partagé — _cache lazy-init au 1er accès
#
# ─────────────────────────────────────────────────────────────────────────────

import os
import json


# ═════════════════════════════════════════════════════════════════════════════
#  EMPLACEMENT DU FICHIER ET DÉFAUTS
# ═════════════════════════════════════════════════════════════════════════════

# Chemin absolu jusqu'à ENTRE-DEUX/hitboxes.json (cf. save_system pour
# l'explication de ce double dirname).
_BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HITBOX_FILE = os.path.join(_BASE_DIR, "hitboxes.json")

# Clé spéciale RÉSERVÉE au joueur (cf. lexique du header).
PLAYER_KEY = "__player__"

# Valeurs de repli si jamais le sprite n'a pas de config.
DEFAULT_HITBOX        = {"w": 36, "h": 40,  "ox": 0, "oy": 0}
DEFAULT_PLAYER_HITBOX = {"w": 90, "h": 104, "ox": 0, "oy": 0}


# ═════════════════════════════════════════════════════════════════════════════
#  CACHE EN MÉMOIRE (chargé au 1er accès)
# ═════════════════════════════════════════════════════════════════════════════

_cache = None


def _load():
    """Charge hitboxes.json en mémoire au PREMIER appel. Les appels suivants
    renvoient le cache directement (pas d'I/O répétée)."""
    global _cache
    if _cache is not None:
        return _cache

    if os.path.exists(HITBOX_FILE):
        try:
            with open(HITBOX_FILE) as f:
                _cache = json.load(f)
        except (json.JSONDecodeError, IOError):
            # Fichier corrompu / permissions → on démarre avec un cache vide
            # plutôt que de planter. set_hitbox() pourra le réécrire proprement.
            _cache = {}
    else:
        _cache = {}
    return _cache


# ═════════════════════════════════════════════════════════════════════════════
#  LECTURE
# ═════════════════════════════════════════════════════════════════════════════

def get_hitbox(sprite_name):
    """Renvoie {"w", "h", "ox", "oy"} pour un sprite ennemi.
    Si le sprite n'a pas de config → COPIE de DEFAULT_HITBOX (cf. header)."""
    data = _load()
    return data.get(sprite_name, DEFAULT_HITBOX.copy())


def get_player_hitbox():
    """Idem mais pour le joueur (via la clé spéciale)."""
    data = _load()
    return data.get(PLAYER_KEY, DEFAULT_PLAYER_HITBOX.copy())


# ═════════════════════════════════════════════════════════════════════════════
#  ÉCRITURE (appelée par l'éditeur quand on ajuste une hitbox visuellement)
# ═════════════════════════════════════════════════════════════════════════════

def set_hitbox(sprite_name, w, h, ox, oy):
    """Enregistre la hitbox d'un sprite ET met à jour le fichier sur disque.

    On met à jour le cache EN MÊME TEMPS pour que les appels get_hitbox()
    suivants voient la nouvelle valeur immédiatement.
    """
    global _cache
    data = _load()
    data[sprite_name] = {"w": w, "h": h, "ox": ox, "oy": oy}
    _cache = data
    with open(HITBOX_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Hitbox '{sprite_name}': {w}×{h} offset({ox},{oy})")


def set_player_hitbox(w, h, ox, oy):
    """Raccourci pour set_hitbox(__player__, ...)."""
    set_hitbox(PLAYER_KEY, w, h, ox, oy)
