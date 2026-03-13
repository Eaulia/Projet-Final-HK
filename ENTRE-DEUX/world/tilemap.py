# ─────────────────────────────────────────
#  ENTRE-DEUX — Plateformes & décors
# ─────────────────────────────────────────

import pygame
from settings import *

class Platform:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def verifier_collision(self, player):
        if player.rect.colliderect(self.rect):
            if player.vy > 0 and player.rect.bottom <= self.rect.top + 15:
                player.rect.bottom = self.rect.top
                player.on_ground = True
                player.vy = 0

    def draw(self, surf, camera):
        pygame.draw.rect(surf, self.color, camera.apply(self.rect))

class Wall:
    def __init__(self, x, y, width, height, visible=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = visible  # True = noir pour débugger, False = invisible

    def verifier_collision(self, player):
        if player.rect.colliderect(self.rect):
            # Vient de la droite → bloque à gauche
            if player.vx > 0:
                player.rect.right = self.rect.left
                player.vx = 0
                print("block")
            # Vient de la gauche → bloque à droite
            elif player.vx < 0:
                player.rect.left = self.rect.right
                player.vx = 0
                print("block")
            # Vient du bas → bloque en haut (plafond)
            elif player.vy < 0:
                player.rect.top = self.rect.bottom
                player.vy = 0
                print("block")

    def draw(self, surf, camera):
        if self.visible:
            pygame.draw.rect(surf, (0, 0, 0), camera.apply(self.rect))