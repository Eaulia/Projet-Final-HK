# ─────────────────────────────────────────
#  ENTRE-DEUX — Boucle principale du jeu
# ─────────────────────────────────────────

import pygame
import settings
from world.editor import Editor
from core.event_handler import x_y_man, man_on
from settings import *
from core.camera import Camera
from entities.player import Player
from entities.enemy import Enemy
from world.tilemap import Platform, Wall
from systems.lighting import LightingSystem
from utils import draw_mouse_coords
from world.collision import check_attack_collisions, check_platform_collisions

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(TITLE)
        self.running = True
        self.clock = pygame.time.Clock()

        self.walls = [
            Wall(0, 590, SCENE_WIDTH, 1000, visible=True),   # Sol
            Wall(0, -20, SCENE_WIDTH, 20, visible=True),     # Plafond
            Wall(0, 0, 20, SCENE_HEIGHT, visible=True),      # Mur gauche
            Wall(SCENE_WIDTH-20, 0, 20, SCENE_HEIGHT, visible=True),  # Mur droit
        ]

        self.player = Player((100, 400))
        self.camera = Camera(SCENE_WIDTH, SCENE_HEIGHT)


        self.enemies = [Enemy(500, 530 - 60)]


        self.platforms = [
            Platform(200, 500, 100, 20, BLANC),
            Platform(300, 400, 100, 20, GRIS),
            Platform(400, 300, 100, 20, BLEU),
        ]

        self.lighting = LightingSystem()
        self.lighting.add_light(300, 480, radius=150, type="torch")
        self.lighting.add_light(600, 380, radius=200, type="torch")

        # Editor en dernier — après lighting !
        self.editor = Editor(self.platforms, self.enemies, self.camera, self.lighting)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000

            # ── Événements ──────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        self.editor.toggle()
                    if event.key == pygame.K_s and self.editor.active:
                        self.editor.save()
                    if event.key == pygame.K_l and self.editor.active:
                        self.editor.load()
                    if event.key == pygame.K_m and self.editor.active:
                        self.editor.change()
                    if event.key == pygame.K_i and self.editor.active:
                        self.editor.toggle_light()

                if self.editor.active:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.editor.light_mode:
                            if event.button == 1:
                                self.editor.handle_light_click(event.pos)
                            if event.button == 3:
                                self.editor.delete_light(event.pos)
                        elif settings.mod == 0:
                            if event.button == 1:
                                self.editor.handle_click(event.pos)
                            if event.button == 3:
                                self.editor.delete_platform(event.pos)
                        else:
                            if event.button == 1:
                                self.editor.handle_click(event.pos)
                            if event.button == 3:
                                self.editor.delete_mob(event.pos)

                # Clic molette → affiche coords monde
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 2:
                        print(f"Monde x:{settings.wx} y:{settings.wy}")

            # ── Mise à jour ──────────────────────────────
            keys = pygame.key.get_pressed()
            man_on()
            x_y_man()

            self.player.mouvement(dt, keys)
            self.camera.update(self.player.rect)

            for enemy in self.enemies:
                enemy.update(dt)

            check_attack_collisions(self.player, self.enemies)
            check_platform_collisions(self.player, self.platforms)

            for wall in self.walls:
                wall.verifier_collision(self.player)

            self.lighting.update()

            # ── Affichage ────────────────────────────────
            self.screen.fill(VIOLET)

            for wall in self.walls:
                if self.camera.is_visible(wall.rect):
                    wall.draw(self.screen, self.camera)

            for platform in self.platforms:
                if self.camera.is_visible(platform.rect):
                    platform.draw(self.screen, self.camera)

            for enemy in self.enemies:
                if self.camera.is_visible(enemy.rect):
                    enemy.draw(self.screen, self.camera)

            self.player.draw(self.screen, self.camera)

            # Lumières — avant HUD
            self.lighting.render(self.screen, self.camera, self.player.rect)

            # HUD et debug — après lumières pour rester lisible
            draw_mouse_coords(self.screen, self.camera)

            if self.editor.active:
                if self.editor.light_mode:
                    self.editor.draw_light_preview(self.screen, pygame.mouse.get_pos())
                elif settings.mod == 0:
                    self.editor.draw_preview(self.screen, pygame.mouse.get_pos())

            pygame.display.flip()