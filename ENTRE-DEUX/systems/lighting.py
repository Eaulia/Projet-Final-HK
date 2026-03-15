import pygame
import random
import  math 
import settings
# ─── Réglages ───────────────────────────
# 
# settings 
#
# ────────────────────────────────────────

class LightingSystem:
    def __init__(self, scale=0.5):
        self.lights = []
        self._cache = {}
        self._scale = scale  # 0.5 = rendu à 50% de la résolution
        self._textures = {
            "player":     pygame.image.load("assets/images/light_player.png").convert(),
            "torch":      pygame.image.load("assets/images/light_medium.png").convert(),
            "large":      pygame.image.load("assets/images/light_large.png").convert(),
            "cool":       pygame.image.load("assets/images/light_cool.png").convert(),
            "dim":        pygame.image.load("assets/images/light_dim.png").convert(),
            "background": pygame.image.load("assets/images/light_background.png").convert(),
        }
        self._darkness = None
        self._ambient = None
        self._screen_size = (0, 0)
        self._low_size = (0, 0)

    def add_light(self, x, y, radius, type="player", flicker = True , flicker_speed = 2):
        self.lights.append({
            "x": x, "y": y, "radius": radius,
            "type": type, "flicker": flicker,
            "flicker_speed": flicker_speed,   # lent=2, normal=5, nerveux=10
            "_phase": random.random() * 6.28,
        })

    def update(self, dt):
        for light in self.lights:
            if light["flicker"]:
                # dt fait tout le travail : pas de pause, pas de blocage
                light["_phase"] += dt * light["flicker_speed"]
                light["_alpha"] = int(210 + 45 * math.sin(light["_phase"]))

    def _get_halo(self, radius, type="torch"):
        key = (radius, type)
        if key not in self._cache:
            tex = self._textures[type]
            size = radius * 2
            halo = pygame.transform.smoothscale(tex, (size, size))
            self._cache[key] = halo
        return self._cache[key]

    def render(self, surf, camera, player_rect):
        screen_w, screen_h = surf.get_size()
        s = self._scale
        low_w = int(screen_w * s)
        low_h = int(screen_h * s)

        if (screen_w, screen_h) != self._screen_size:
            self._screen_size = (screen_w, screen_h)
            self._low_size = (low_w, low_h)
            self._darkness = pygame.Surface((low_w, low_h))
            self._ambient = pygame.Surface((low_w, low_h))

        self._darkness.fill((0, 0, 0))

        # Joueur
        sx = int((player_rect.centerx - camera.offset_x) * s)
        sy = int((player_rect.centery - camera.offset_y) * s)
        r_player = int(settings.RAYON_JOUEUR * s)
        halo = self._get_halo(r_player, "player")
        self._darkness.blit(halo, (sx - r_player, sy - r_player),
                            special_flags=pygame.BLEND_RGB_ADD)

        # Torches
        for light in self.lights:
            lx = int((light["x"] - camera.offset_x) * s)
            ly = int((light["y"] - camera.offset_y) * s)
            r  = int(light["radius"] * s)

            if lx + r < 0 or lx - r > low_w or ly + r < 0 or ly - r > low_h:
                continue

            halo = self._get_halo(r, light["type"])

            if "_alpha" in light:
                halo = halo.copy()
                a = light["_alpha"]
                halo.fill((a, a, a), special_flags=pygame.BLEND_RGB_MULT)

            self._darkness.blit(halo, (lx - r, ly - r),
                                special_flags=pygame.BLEND_RGB_ADD)

        # Ambiance
        self._ambient.fill((settings.FOND_ALPHA, settings.FOND_ALPHA,settings.FOND_ALPHA))
        self._darkness.blit(self._ambient, (0, 0), special_flags=pygame.BLEND_RGB_MAX)

        # Upscale et application
        scaled = pygame.transform.smoothscale(self._darkness, (screen_w, screen_h))
        surf.blit(scaled, (0, 0), special_flags=pygame.BLEND_RGB_MULT)