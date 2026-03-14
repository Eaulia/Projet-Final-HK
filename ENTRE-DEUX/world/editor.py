import pygame
import json
import settings
from entities.enemy import *
from settings import *
from world.tilemap import Platform

class Editor:
    def __init__(self, platforms,enemies, camera):
        self.platforms = platforms
        self.enemies = enemies 
        self.camera = camera
        self.active = False       # mode éditeur ON/OFF
        self.first_point = None   # premier clic
        self.preview = None       # rectangle en cours de dessin
        self.mod= False

    def toggle(self):
        self.active = not self.active
        self.first_point = None
        print("Éditeur :", "ON" if self.active else "OFF")
    
    def change(self):
        self.first_point = None
        self.mod = not self.mod
        if self.mod:
            settings.mod = 1
        else:
            settings.mod = 0
        
        print("Éditeur : mob ", "ON" if self.mod else "OFF")

    def handle_click(self, mouse_pos):
        print("oui")
        # Convertir position écran → position monde
        wx = int(mouse_pos[0] + self.camera.offset_x)
        wy = int(mouse_pos[1] + self.camera.offset_y)

        if self.mod:
            self.enemies.append(Enemy(wx, wy))
            self.first_point = None

        if self.first_point is None:
            # Premier clic → mémoriser le coin
            self.first_point = (wx, wy)
            print(f"Premier point : {self.first_point}")
            return
        

        
        if self.first_point is not None:
            print('ok')
            # Deuxième clic → créer la plateforme
            x1, y1 = self.first_point
            x2, y2 = wx, wy
            x = min(x1, x2)
            y = min(y1, y2)
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            print('ok2')
            if w > 0 and h > 0:
                self.platforms.append(Platform(x, y, w, h, BLANC))
                print(f"Plateforme créée : x={x} y={y} w={w} h={h}")
            print("ok3")
            self.first_point = None

    def delete_platform(self, mouse_pos):
        """Clic droit pour supprimer une plateforme"""
        wx = int(mouse_pos[0] + self.camera.offset_x)
        wy = int(mouse_pos[1] + self.camera.offset_y)
        point = pygame.Rect(wx, wy, 1, 1)
        self.platforms[:] = [p for p in self.platforms 
                              if not p.rect.colliderect(point)]
        
    def delete_mob(self, mouse_pos):
        """Clic droit pour supprimer un mob"""
        wx = int(mouse_pos[0] + self.camera.offset_x)
        wy = int(mouse_pos[1] + self.camera.offset_y)
        point = pygame.Rect(wx, wy, 1, 1)
        self.enemies[:] = [p for p in self.enemies 
                                if not p.rect.colliderect(point)]

    def draw_preview(self, surf, mouse_pos):
        """Affiche le rectangle en cours de construction"""
        if self.first_point is None:
            return
        wx = int(mouse_pos[0] + self.camera.offset_x)
        wy = int(mouse_pos[1] + self.camera.offset_y)
        x = min(self.first_point[0], wx) - int(self.camera.offset_x)
        y = min(self.first_point[1], wy) - int(self.camera.offset_y)
        w = abs(wx - self.first_point[0])
        h = abs(wy - self.first_point[1])
        pygame.draw.rect(surf, (100, 200, 255), (x, y, w, h), 2)

    def save(self, filename="map.json"):
        data = [
            {"x": p.rect.x, "y": p.rect.y,
             "w": p.rect.width, "h": p.rect.height}
            for p in self.platforms
        ]
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Map sauvegardée ({len(data)} plateformes)")

    def load(self, filename="map.json"):
        try:
            with open(filename) as f:
                data = json.load(f)
            self.platforms.clear()
            for p in data:
                self.platforms.append(
                    Platform(p["x"], p["y"], p["w"], p["h"], BLANC)
                )
            print(f"Map chargée ({len(data)} plateformes)")
        except FileNotFoundError:
            print("Pas de map sauvegardée")