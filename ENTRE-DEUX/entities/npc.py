# ─────────────────────────────────────────
#  ENTRE-DEUX — PNJ (personnages non-joueurs)
# ─────────────────────────────────────────

import os
import pygame
from entities.animation import Animation
from systems.hitbox_config import get_hitbox

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PNJ_DIR   = os.path.join(_BASE_DIR, "assets", "images", "pnj")
os.makedirs(PNJ_DIR, exist_ok=True)


def list_pnj_sprites():
    """Liste les sprites disponibles dans assets/images/pnj/."""
    sprites = []
    if not os.path.isdir(PNJ_DIR):
        return sprites
    for f in sorted(os.listdir(PNJ_DIR)):
        full = os.path.join(PNJ_DIR, f)
        if f.endswith((".png", ".jpg")):
            sprites.append(f)
        elif os.path.isdir(full):
            frames = [g for g in sorted(os.listdir(full)) if g.endswith((".png", ".jpg"))]
            if frames:
                sprites.append(f)
    return sprites


def _charger_frames_pnj(sprite_name):
    """Charge les images pour un sprite PNJ (unique ou animé)."""
    chemin = os.path.join(PNJ_DIR, sprite_name)
    if os.path.isdir(chemin):
        fichiers = sorted(
            (g for g in os.listdir(chemin) if g.endswith((".png", ".jpg"))),
            key=lambda s: int("".join(filter(str.isdigit, s)) or "0"),
        )
        return [pygame.image.load(os.path.join(chemin, ff)) for ff in fichiers]
    if os.path.exists(chemin):
        return [pygame.image.load(chemin)]
    return []


class PNJ:
    """
    Personnage non-joueur positionné dans la scène.

    Il peut engager un dialogue quand le joueur s'approche et appuie sur E.

    dialogues : liste de "conversations".
        Chaque conversation est une liste de lignes :  [(texte, orateur), ...]
        La dernière conversation se répète indéfiniment.

    sprite_name : nom du fichier ou dossier dans assets/images/pnj/
                  Si None ou introuvable, affiche un rectangle de fallback.
    """

    RAYON_INTERACTION = 90
    COULEUR_FALLBACK  = (180, 160, 230)

    def __init__(self, x, y, nom, dialogues, sprite_name=None,
                 dialogue_mode="boucle_dernier"):
        self.nom           = nom
        self.sprite_name   = sprite_name
        self._dialogues    = dialogues
        self._conv_idx     = 0
        # "boucle_dernier" = répète la dernière phrase, "restart" = recommence tout
        self.dialogue_mode = dialogue_mode

        # Chargement du sprite
        self._frames = []
        self._anim   = None
        if sprite_name:
            self._frames = _charger_frames_pnj(sprite_name)
        if self._frames:
            self._anim = Animation(self._frames, img_dur=8, loop=True)
            hb = get_hitbox(sprite_name) if sprite_name else None
            if hb:
                self.rect = pygame.Rect(x, y, hb["w"], hb["h"])
            else:
                img = self._frames[0]
                self.rect = pygame.Rect(x, y, img.get_width(), img.get_height())
        else:
            self.rect = pygame.Rect(x, y, 34, 54)

        self._police = None

    # ── Détection de proximité ────────────────────────────────────────────

    def peut_interagir(self, joueur_rect):
        dist_x = abs(self.rect.centerx - joueur_rect.centerx)
        dist_y = abs(self.rect.centery - joueur_rect.centery)
        return dist_x < self.RAYON_INTERACTION and dist_y < self.RAYON_INTERACTION

    # ── Dialogue ──────────────────────────────────────────────────────────

    def conversation_actuelle(self):
        """
        Retourne la liste de lignes de la prochaine conversation.

        boucle_dernier : la dernière conversation se répète indéfiniment.
        restart        : après la dernière, recommence depuis le début.
        """
        if not self._dialogues:
            return []

        conv = self._dialogues[self._conv_idx]
        if self.dialogue_mode == "restart":
            self._conv_idx = (self._conv_idx + 1) % len(self._dialogues)
        else:
            # boucle_dernier — bloque sur la dernière
            self._conv_idx = min(self._conv_idx + 1, len(self._dialogues) - 1)
        return conv

    def reset_dialogue(self):
        self._conv_idx = 0

    # ── Mise à jour ──────────────────────────────────────────────────────

    def update(self):
        if self._anim:
            self._anim.update()

    # ── Rendu ─────────────────────────────────────────────────────────────

    def _init_police(self):
        if self._police is None:
            self._police = pygame.font.SysFont("Consolas", 12)

    def draw(self, surf, camera, joueur_rect=None):
        self._init_police()
        rect_ecran = camera.apply(self.rect)

        if self._anim and self._frames:
            img = self._anim.img()
            surf.blit(img, (rect_ecran.x, rect_ecran.y))
        else:
            # Fallback : rectangle coloré si pas de sprite
            pygame.draw.rect(surf, self.COULEUR_FALLBACK, rect_ecran)
            pygame.draw.rect(surf, (255, 255, 255), rect_ecran, 1)

        # Nom flottant au-dessus du personnage
        nom_surf = self._police.render(self.nom, True, (215, 200, 255))
        surf.blit(nom_surf, (
            rect_ecran.centerx - nom_surf.get_width() // 2,
            rect_ecran.top - 16,
        ))

        # Indicateur d'interaction si le joueur est proche
        if joueur_rect and self.peut_interagir(joueur_rect):
            ind = self._police.render("[ E ]", True, (255, 215, 70))
            surf.blit(ind, (
                rect_ecran.centerx - ind.get_width() // 2,
                rect_ecran.top - 30,
            ))

    # ── Sérialisation (éditeur) ───────────────────────────────────────────

    def to_dict(self):
        return {
            "type":          "pnj",
            "x":             self.rect.x,
            "y":             self.rect.y,
            "nom":           self.nom,
            "sprite_name":   self.sprite_name,
            "dialogues":     self._dialogues,
            "dialogue_mode": self.dialogue_mode,
        }

    @staticmethod
    def from_dict(data):
        return PNJ(
            data["x"], data["y"],
            data.get("nom", "PNJ"),
            data.get("dialogues", []),
            sprite_name=data.get("sprite_name"),
            dialogue_mode=data.get("dialogue_mode", "boucle_dernier"),
        )
