# ─────────────────────────────────────────
#  ENTRE-DEUX — Boucle principale du jeu
# ─────────────────────────────────────────

import pygame
import settings
from settings import *
from core.camera import Camera
from entities.player import Player
from entities.enemy import Enemy
from world.tilemap import Platform
from utils import draw_mouse_coords
from world.tilemap import Platform, Wall  # ← ajouter Wall à l'import
from world.collision import check_attack_collisions, check_platform_collisions

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(TITLE)
        self.running = True
        self.clock = pygame.time.Clock()
        self.walls = [
            # Sol
            Wall(0,590, SCENE_WIDTH, 1000, visible=True),
            # Plafond
            Wall(0, -20, SCENE_WIDTH, 20, visible=True),
            # Mur gauche
            Wall(0,0, 20, SCENE_HEIGHT, visible=True),
            # Mur droit
            Wall(SCENE_WIDTH-20,0, 20, SCENE_HEIGHT, visible=True),
        ]

        self.player = Player((40, 0))
        self.camera = Camera(SCENE_WIDTH, SCENE_HEIGHT)
        self.enemies = [Enemy(500, 530 - 60)]
        self.platforms = [
            Platform(200, 500, 100, 20, BLANC),
            Platform(300, 400, 100, 20, GRIS),
            Platform(400, 300, 100, 20, BLEU),
        ]

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000

            # Événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Mise à jour
            keys = pygame.key.get_pressed()
            self.player.mouvement(dt, keys)
            self.camera.update(self.player.rect)
            clic_gauche, clic_molette, clic_droit = pygame.mouse.get_pressed()
            if clic_molette:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 2:  # 2 = clic molette
                        wx = settings.wx
                        wy = settings.wy
                        print(wx,wy)



            for enemy in self.enemies:
                enemy.update(dt)

            check_attack_collisions(self.player, self.enemies)
            check_platform_collisions(self.player, self.platforms)
            

            # Affichage
            self.screen.fill(VIOLET)
            for wall in self.walls:
                if self.camera.is_visible(wall.rect):
                    wall.verifier_collision(self.player)
                    wall.draw(self.screen, self.camera)

            for platform in self.platforms:
                if self.camera.is_visible(platform.rect):
                    platform.draw(self.screen, self.camera)

            for enemy in self.enemies:
                if self.camera.is_visible(enemy.rect):
                    enemy.draw(self.screen, self.camera)

            self.player.draw(self.screen, self.camera)
            

            draw_mouse_coords(self.screen, self.camera)

            pygame.display.flip()
