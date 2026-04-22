# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Boss (hérite d'Enemy) — STUB / EMBRYON
# ─────────────────────────────────────────────────────────────────────────────
#
#  ÉTAT ACTUEL : EMBRYON (pas encore branché à l'histoire)
#  -------------------------------------------------------
#  Cette classe est une COQUILLE pour les futurs boss du jeu. Elle hérite
#  de Enemy (entities/enemy.py) → elle profite déjà de tout le système de
#  combat / déplacement / collisions. Il restera juste à overrider les
#  comportements spécifiques boss-par-boss (patterns d'attaque, phases...).
#
#  USAGE PRÉVU
#  -----------
#       class BossOmbre(Boss):
#           def __init__(self, x, y):
#               super().__init__(x, y)
#               self.hp = 12              # plus dur qu'un boss générique
#               self.phase = 1
#
#           def update(self, dt):
#               super().update(dt)
#               if self.hp < 6 and self.phase == 1:
#                   self.phase = 2        # passe en phase enragée
#                   self.speed *= 1.5
#               ...
#
#  Petit lexique :
#     - héritage     = `class Boss(Enemy)` → Boss est UNE SORTE de Enemy.
#                      Il a tout ce que Enemy a (rect, hp, update...) et
#                      peut en plus avoir ses propres méthodes / overrides.
#     - super()      = "appelle la méthode du parent". super().__init__(x, y)
#                      = "fais d'abord ce que Enemy.__init__ fait, puis
#                      j'ajoute mes ajustements".
#     - phase        = entier qui mémorise dans QUELLE PHASE est le boss.
#                      Pattern classique : phase 1 = attaque normale,
#                      phase 2 = "il devient fou et plus rapide" à 50 % PV.
#     - stub         = "embryon" — coquille vide qui réserve l'API en
#                      attendant l'implémentation réelle.
#
#  POURQUOI 120×120 PX ?
#  ---------------------
#  Pour qu'un boss soit visuellement IMPRESSIONNANT, il doit faire bien
#  plus gros qu'un ennemi standard. 120 px ≈ 4 fois la taille d'un slime.
#  À ajuster pour chaque boss spécifique en fonction de son sprite.
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  PAS ENCORE. Quand un boss sera scénarisé, on en créera une instance
#  dans la scène concernée et game.py le mettra à jour comme un ennemi.
#
# ─────────────────────────────────────────────────────────────────────────────

import pygame
from settings import *
from entities.enemy import Enemy


class Boss(Enemy):
    """Squelette générique de boss. À overrider par boss spécifique."""

    def __init__(self, x, y):
        super().__init__(x, y)                         # tout l'init d'Enemy
        self.rect  = pygame.Rect(x, y, 120, 120)       # plus grand qu'un ennemi normal
        self.hp    = 5                                 # plus de PV qu'un mob standard
        self.phase = 1                                 # phase courante (cf. lexique)

    # À compléter selon les boss de l'histoire
    # (override de update(), patterns d'attaque, transitions de phase...)
