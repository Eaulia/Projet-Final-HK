# ─────────────────────────────────────────
#  ENTRE-DEUX — Ennemi de base
# ─────────────────────────────────────────

import pygame
from settings import *
from entities.animation import Animation
from utils import *

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 60)
        self.vx = 120
        self.alive = True
        self.on_ground = True
        self.idle_anim = Animation([
            pygame.image.load(find_file("monstre_perdu.png"))
        ],img_dur=20)

    def update(self, dt):
        self.rect.x += self.vx * dt

        # Change de direction s'il touche un bord
        if self.rect.left < 0 or self.rect.right > SCENE_WIDTH-20:
            self.vx *= -1


    def draw(self, surf, camera):
        if self.alive:
            img = self.idle_anim.img()
            if self.vx < 0:
                img = pygame.transform.flip(img, True, False)
            self.idle_anim.update()
            surf.blit(img, camera.apply(self.rect))
            #pygame.draw.rect(surf, ROUGE, camera.apply(self.rect))
