# ─────────────────────────────────────────
#  ENTRE-DEUX — Caméra
# ─────────────────────────────────────────
import pygame
import settings
from settings import WIDTH, HEIGHT


class Camera:
    def __init__(self, scene_width, scene_height):
        self.offset_x     = 0
        self.offset_y     = 0
        self.scene_width  = scene_width
        self.scene_height = scene_height
        self.y_offset     = 150

        # Cache de la taille écran — évite get_surface() à chaque appel
        self._sw = WIDTH
        self._sh = HEIGHT

        # ── Caméra libre (éditeur) ──
        self.free_mode = False
        self._drag_active = False
        self._drag_prev = None
        self.zoom = 1.0  # réservé pour plus tard

    def update(self, target_rect):
        # Mise à jour du cache taille écran une fois par frame
        surf = pygame.display.get_surface()
        if surf:
            self._sw, self._sh = surf.get_size()

        if self.free_mode:
            # En mode libre, pas de suivi du joueur
            return

        target_x = target_rect.centerx - self._sw // 2
        target_y = target_rect.centery - self._sh // 2 + self.y_offset

        self.offset_x += (target_x - self.offset_x) * 0.1
        self.offset_y += (target_y - self.offset_y) * 0.1

        max_y = settings.GROUND_Y + 40 - self._sh
        min_y = settings.CEILING_Y - self._sh // 2

        self.offset_x = max(0, min(self.offset_x, self.scene_width - self._sw))
        self.offset_y = max(min_y, min(self.offset_y, max(0, max_y)))

    def start_drag(self, pos):
        """Début du drag caméra libre (clic molette)."""
        self._drag_active = True
        self._drag_prev = pos

    def update_drag(self, pos):
        """Mise à jour du drag caméra libre."""
        if not self._drag_active or self._drag_prev is None:
            return
        dx = pos[0] - self._drag_prev[0]
        dy = pos[1] - self._drag_prev[1]
        self.offset_x -= dx
        self.offset_y -= dy
        self._drag_prev = pos

    def stop_drag(self):
        """Fin du drag caméra libre."""
        self._drag_active = False
        self._drag_prev = None

    def pan_scroll(self, direction):
        """Molette en mode libre : déplace la caméra verticalement."""
        self.offset_y -= direction * 60

    def apply(self, rect):
        return pygame.Rect(
            rect.x - int(self.offset_x),
            rect.y - int(self.offset_y),
            rect.width,
            rect.height,
        )

    def is_visible(self, rect):
        """Test de visibilité sans appel à get_surface()."""
        return (rect.right  > self.offset_x and
                rect.left   < self.offset_x + self._sw and
                rect.bottom > self.offset_y and
                rect.top    < self.offset_y + self._sh)
