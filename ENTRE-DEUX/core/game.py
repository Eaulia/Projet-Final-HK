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
        self.enemies = [Enemy(500, 530 - 38)]
        self.platforms = [
            Platform(200, 500, 100, 20, BLANC),
            Platform(300, 400, 100, 20, GRIS),
            Platform(400, 300, 100, 20, BLEU),
        ]
        self.editor = Editor(self.platforms,self.enemies, self.camera)
        
        

        
   
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000

            # Événements
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

                if self.editor.active:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if mod == 0:
                            if event.button == 1:  # clic gauche → placer
                                self.editor.handle_click(event.pos)
                            if event.button == 3:  # clic droit → supprimer
                                self.editor.delete_platform(event.pos)
                        else:
                            if event.button == 1:  # clic gauche → placer
                                self.editor.handle_click(event.pos)
                            if event.button == 3:  # clic droit → supprimer
                                self.editor.delete_mob(event.pos)


            # Mise à jour
            keys = pygame.key.get_pressed()
            man_on ()
            """
            if settings.manette:
                for i in range(settings.manette.get_numaxes()):
                    val = settings.manette.get_axis(i)
                    if abs(val) > 0.1:
                        print(f"Axe {i} = {val:.2f}")
                for i in range(settings.manette.get_numbuttons()):
                    if settings.manette.get_button(i):
                        print(f"Bouton {i} pressé")
            """
            x_y_man ()
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
            if self.editor.active:
                if settings.mod == 0:
                    self.editor.draw_preview(self.screen, pygame.mouse.get_pos())

            pygame.display.flip()
