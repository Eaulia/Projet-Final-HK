# ─────────────────────────────────────────
#  ENTRE-DEUX — Plateformes & décors
# ─────────────────────────────────────────

import pygame
from settings import *
from world.collision import resoudre_collision

_cache_images = {}   # évite de recharger le même fichier plusieurs fois


class Platform:
    """Surface sur laquelle on peut marcher. Pousse l'entité quelle que soit sa direction."""

    def __init__(self, x, y, width, height, color):
        self.rect  = pygame.Rect(x, y, width, height)
        self.color = color

    def verifier_collision(self, entite):
        resoudre_collision(entite, self.rect, mode_mur=False)

    def draw(self, surf, camera):
        pygame.draw.rect(surf, self.color, camera.apply(self.rect))


class Wall:
    """Mur qui bloque selon la direction de déplacement (évite les projections parasites)."""

    def __init__(self, x, y, width, height, visible=False,
                 player_only=False, is_border=False):
        self.rect        = pygame.Rect(x, y, width, height)
        self.visible     = visible
        self.player_only = player_only  # si True, les ennemis passent au travers
        self.is_border   = is_border    # bordure de scène, ignorée par le raycasting

    def verifier_collision(self, entite):
        resoudre_collision(entite, self.rect, mode_mur=True)

    def draw(self, surf, camera):
        if self.visible:
            pygame.draw.rect(surf, (0, 0, 0), camera.apply(self.rect))


class Decor:
    """Élément de décor placé dans le monde. Peut bloquer le joueur si collision=True.

    collision_box : (ox, oy, w, h) relatif au coin haut-gauche du décor.
                    Si None, la hitbox = le rect de l'image entière.
    """

    def __init__(self, x, y, chemin_image, nom_sprite, collision=False,
                 echelle=1.0, collision_box=None):
        self.nom_sprite = nom_sprite
        self.collision  = collision
        self.echelle    = echelle

        if chemin_image not in _cache_images:
            _cache_images[chemin_image] = pygame.image.load(chemin_image)
        base = _cache_images[chemin_image]

        if echelle != 1.0:
            w = max(1, int(base.get_width()  * echelle))
            h = max(1, int(base.get_height() * echelle))
            self.image = pygame.transform.scale(base, (w, h))
        else:
            self.image = base

        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

        # Hitbox personnalisée (ox, oy, w, h) relative au rect — None = image entière
        self.collision_box = collision_box

    @property
    def collision_rect(self):
        """Retourne le rect de collision dans le monde."""
        if self.collision_box:
            ox, oy, cw, ch = self.collision_box
            return pygame.Rect(self.rect.x + ox, self.rect.y + oy, cw, ch)
        return self.rect

    def verifier_collision(self, entite):
        if self.collision:
            resoudre_collision(entite, self.collision_rect, mode_mur=False)

    def draw(self, surf, camera):
        surf.blit(self.image, camera.apply(self.rect))

    def to_dict(self):
        d = {"x": self.rect.x, "y": self.rect.y,
             "sprite": self.nom_sprite, "collision": self.collision,
             "echelle": self.echelle}
        if self.collision_box:
            d["collision_box"] = list(self.collision_box)
        return d
