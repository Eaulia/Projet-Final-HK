# ─────────────────────────────────────────
#  ENTRE-DEUX — Musique de fond
# ─────────────────────────────────────────

import pygame

_current = None


def jouer(chemin, boucle=-1, volume=0.5):
    """Lance une musique. Ne recharge pas si c'est déjà en cours."""
    global _current
    if chemin == _current:
        return
    try:
        pygame.mixer.music.load(chemin)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(boucle)
        _current = chemin
    except Exception:
        pass


def arreter():
    global _current
    pygame.mixer.music.stop()
    _current = None


def volume(v):
    pygame.mixer.music.set_volume(max(0.0, min(1.0, v)))
