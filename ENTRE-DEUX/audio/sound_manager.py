# ─────────────────────────────────────────
#  ENTRE-DEUX — Effets sonores
# ─────────────────────────────────────────

import pygame

_sons = {}


def charger(nom, chemin):
    """Charge un son et le stocke sous un nom."""
    try:
        _sons[nom] = pygame.mixer.Sound(chemin)
    except Exception:
        pass


def jouer(nom, volume=1.0):
    """Joue un son par son nom."""
    son = _sons.get(nom)
    if son:
        son.set_volume(max(0.0, min(1.0, volume)))
        son.play()


def arreter(nom):
    son = _sons.get(nom)
    if son:
        son.stop()
