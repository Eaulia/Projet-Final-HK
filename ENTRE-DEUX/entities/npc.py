# ─────────────────────────────────────────
#  ENTRE-DEUX — PNJ (personnages non-joueurs)
# ─────────────────────────────────────────

import pygame


class PNJ:
    """
    Personnage non-joueur positionné dans la scène.

    Il peut engager un dialogue quand le joueur s'approche et appuie sur E.

    dialogues : liste de "conversations".
        Chaque conversation est une liste de lignes :  [(texte, orateur), ...]
        La dernière conversation se répète indéfiniment.

    Exemple :
        PNJ(300, 450, "Nimbus", [
            [("Tu es tombé de bien haut.", "Nimbus"), ("...", "Nimbus")],
            [("Je t'attendais.", "Nimbus")],
        ])
    """

    RAYON_INTERACTION = 90    # distance en pixels pour déclencher le dialogue
    COULEUR_DEFAUT    = (180, 160, 230)

    def __init__(self, x, y, nom, dialogues, couleur=None):
        self.rect      = pygame.Rect(x, y, 34, 54)
        self.nom       = nom
        self.couleur   = couleur or self.COULEUR_DEFAUT
        self._dialogues = dialogues      # liste de conversations
        self._conv_idx  = 0              # conversation en cours

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
        Une fois la dernière atteinte, elle se répète.
        """
        if not self._dialogues:
            return []

        conv = self._dialogues[self._conv_idx]
        # Avance mais reste bloqué sur la dernière conversation
        self._conv_idx = min(self._conv_idx + 1, len(self._dialogues) - 1)
        return conv

    # ── Rendu ─────────────────────────────────────────────────────────────

    def _init_police(self):
        if self._police is None:
            self._police = pygame.font.SysFont("Consolas", 12)

    def draw(self, surf, camera, joueur_rect=None):
        self._init_police()
        rect_ecran = camera.apply(self.rect)

        # Corps du PNJ (rectangle coloré — remplacé par un sprite plus tard)
        pygame.draw.rect(surf, self.couleur, rect_ecran)
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
            "type":    "pnj",
            "x":       self.rect.x,
            "y":       self.rect.y,
            "nom":     self.nom,
            "couleur": list(self.couleur),
        }
