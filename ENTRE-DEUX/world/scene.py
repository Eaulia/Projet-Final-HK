# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Scene (zone du jeu) — STUB / EMBRYON
# ─────────────────────────────────────────────────────────────────────────────
#
#  ÉTAT ACTUEL : EMBRYON (pas encore branché au jeu)
#  -------------------------------------------------
#  Cette classe est une SQUELETTE en attente d'utilisation. Aujourd'hui,
#  l'organisation des objets de la scène (plateformes, ennemis, PNJ...)
#  vit directement dans core/game.py et world/editor.py. Cette classe
#  Scene + son SceneManager (à côté) sont là pour le jour où on voudra
#  cloisonner ça proprement.
#
#  À QUOI ÇA SERVIRA (à terme) ?
#  -----------------------------
#  Une Scene = "une zone du monde" : un nom, une liste de plateformes,
#  d'ennemis, de PNJ, de compagnons. On en chargera plusieurs (forêt,
#  village, donjon...) et on basculera de l'une à l'autre via le
#  SceneManager.
#
#  POURQUOI LE GARDER S'IL N'EST PAS UTILISÉ ?
#  -------------------------------------------
#  Pour 2 raisons :
#       1) Documenter l'INTENTION d'architecture pour qu'un nouveau
#          développeur (ou toi dans 6 mois) sache où brancher ça.
#       2) Réserver l'API : update(dt, player) et draw(surf) ont la
#          même signature que partout ailleurs dans le jeu, donc le
#          jour où on l'utilise, ça se branche sans rien casser.
#
#  Petit lexique :
#     - stub        = "embryon de code" : la coquille vide d'une fonctionnalité
#                     qu'on prévoit d'implémenter plus tard. Permet de fixer
#                     l'API tôt même si l'intérieur est creux.
#     - scène       = en jeu vidéo, une zone autonome (≠ "scène" au sens
#                     théâtral). Chaque scène a son propre décor et ses
#                     propres ennemis.
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D22]  conventions update/draw — chaque "système" du jeu expose ces
#                                       deux méthodes pour s'intégrer à la
#                                       boucle principale de game.py.
#
# ─────────────────────────────────────────────────────────────────────────────

import pygame
from settings import *


class Scene:
    """Une zone du jeu (forêt, village, donjon...) — STUB."""

    def __init__(self, name):
        self.name       = name
        self.platforms  = []     # plateformes (sols, marches...)
        self.enemies    = []     # ennemis présents dans cette scène
        self.npcs       = []     # PNJ (à compléter)
        self.companions = []     # compagnons spawnés ici (à compléter)

    def update(self, dt, player):
        """Met à jour tous les objets de la scène. Appelée à chaque frame."""
        for enemy in self.enemies:
            enemy.update(dt)
        # PNJ et compagnons : à brancher quand on adoptera cette architecture.

    def draw(self, surf):
        """Dessine la scène sur `surf`. Appelée à chaque frame."""
        for platform in self.platforms:
            platform.draw(surf)
        for enemy in self.enemies:
            enemy.draw(surf)
        for npc in self.npcs:
            pass  # À compléter
        for companion in self.companions:
            pass  # À compléter
