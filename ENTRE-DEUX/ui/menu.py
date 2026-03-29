# ─────────────────────────────────────────
#  ENTRE-DEUX — Menus (titre, pause, fin)
# ─────────────────────────────────────────

import math
import random
import pygame


# ── Particule décorative ──────────────────────────────────────────────────────

class Particule:
    """
    Petite lueur qui flotte vers le haut dans le fond du menu titre.
    Inspiré de l'ambiance Hollow Knight — poussière lumineuse dans l'obscurité.
    """

    COULEURS = [
        (180, 160, 255),  # violet clair
        (255, 220, 100),  # doré
        (140, 200, 255),  # bleu-blanc
        (200, 255, 200),  # vert très pâle
    ]

    def __init__(self, largeur, hauteur):
        self._w = largeur
        self._h = hauteur
        self._respawn()

    def _respawn(self):
        self.x      = random.uniform(0, self._w)
        self.y      = random.uniform(0, self._h)
        self.vx     = random.uniform(-12, 12)
        self.vy     = random.uniform(-30, -8)   # remonte lentement
        self.rayon  = random.uniform(1.0, 2.5)
        self.alpha  = random.randint(40, 160)
        self.couleur = random.choice(self.COULEURS)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Quand la particule sort de l'écran, elle réapparaît en bas
        if self.y < -4 or self.x < -4 or self.x > self._w + 4:
            self.x = random.uniform(0, self._w)
            self.y = self._h + 4
            self.vx = random.uniform(-12, 12)
            self.vy = random.uniform(-30, -8)

    def draw(self, surf):
        taille = int(self.rayon * 2) + 2
        s = pygame.Surface((taille, taille), pygame.SRCALPHA)
        centre = (taille // 2, taille // 2)
        pygame.draw.circle(s, (*self.couleur, self.alpha), centre, int(self.rayon))
        surf.blit(s, (int(self.x) - taille // 2, int(self.y) - taille // 2))


# ── Classe Menu ───────────────────────────────────────────────────────────────

class Menu:
    """
    Menu réutilisable pour le titre, la pause et l'écran de fin.

    style="titre"   → fond sombre total + particules flottantes
                       (utilisé quand il n'y a rien derrière)

    style="panneau" → petit cadre semi-transparent centré sur le fond actuel
                       (utilisé pour la pause et le game over — on voit le jeu derrière)
    """

    def __init__(self, options, title="", style="panneau",
                 offset_x=0, offset_y=0):
        self.options   = options
        self.title     = title
        self.style     = style
        self.selection = 0

        # Décalage du menu par rapport au centre (en pixels)
        # offset_x > 0 → décale vers la droite, offset_y > 0 → vers le bas
        self.offset_x = offset_x
        self.offset_y = offset_y

        self._particules    = []
        self._police_titre  = None
        self._police_option = None
        self._police_sous   = None

    # ── Initialisation lazy ───────────────────────────────────────────────

    def _init_polices(self):
        if self._police_titre is None:
            self._police_titre  = pygame.font.SysFont("Consolas", 46, bold=True)
            self._police_option = pygame.font.SysFont("Consolas", 21)
            self._police_sous   = pygame.font.SysFont("Consolas", 13)

    def _init_particules(self, w, h):
        if not self._particules:
            self._particules = [Particule(w, h) for _ in range(45)]

    # ── Mise à jour (appeler chaque frame) ────────────────────────────────

    def update(self, dt):
        surf = pygame.display.get_surface()
        if surf:
            self._init_particules(*surf.get_size())
        for p in self._particules:
            p.update(dt)

    # ── Entrées clavier ───────────────────────────────────────────────────

    def handle_key(self, key):
        if key == pygame.K_UP:
            self.selection = (self.selection - 1) % len(self.options)
        elif key == pygame.K_DOWN:
            self.selection = (self.selection + 1) % len(self.options)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            return self.options[self.selection]
        return None

    # ── Rendu ─────────────────────────────────────────────────────────────

    def draw(self, surf):
        self._init_polices()
        w, h = surf.get_size()

        if self.style == "titre":
            self._dessiner_ecran_titre(surf, w, h)
        else:
            self._dessiner_panneau(surf, w, h)

    def _dessiner_ecran_titre(self, surf, w, h):
        # Fond très sombre — comme les profondeurs de l'Entremonde
        fond = pygame.Surface((w, h), pygame.SRCALPHA)
        fond.fill((6, 6, 18, 245))
        surf.blit(fond, (0, 0))

        # Lueurs flottantes
        self._init_particules(w, h)
        for p in self._particules:
            p.draw(surf)

        cx = w // 2 + self.offset_x
        cy_titre = h // 4 + self.offset_y

        # Titre avec effet de glow (ombre décalée + texte principal)
        if self.title:
            ombre = self._police_titre.render(self.title, True, (60, 40, 120))
            surf.blit(ombre, (cx - ombre.get_width() // 2 + 2, cy_titre + 2))

            titre_surf = self._police_titre.render(self.title, True, (210, 190, 255))
            surf.blit(titre_surf, (cx - titre_surf.get_width() // 2, cy_titre))

        # Ligne décorative sous le titre
        lx1 = cx - w // 4
        lx2 = cx + w // 4
        ly  = cy_titre + 68
        pygame.draw.line(surf, (80, 60, 160), (lx1, ly), (lx2, ly), 1)

        # Petits losanges aux extrémités de la ligne
        for lx in (lx1, lx2):
            points = [(lx, ly - 4), (lx + 4, ly), (lx, ly + 4), (lx - 4, ly)]
            pygame.draw.polygon(surf, (130, 100, 220), points)

        # Options
        debut_y = h // 2 - 10 + self.offset_y
        for i, option in enumerate(self.options):
            if i == self.selection:
                couleur    = (255, 215, 70)     # doré sélectionné
                indicateur = "◆"
            else:
                couleur    = (150, 135, 200)    # violet pâle
                indicateur = " "

            opt_surf = self._police_option.render(f" {indicateur}  {option}", True, couleur)
            surf.blit(opt_surf, (cx - opt_surf.get_width() // 2, debut_y + i * 42))

        # Petite indication en bas
        aide = self._police_sous.render("↑↓ Naviguer   Entrée Valider", True, (70, 60, 110))
        surf.blit(aide, (cx - aide.get_width() // 2, h - 30))

    def _dessiner_panneau(self, surf, w, h):
        """
        Panneau flottant — le jeu reste visible en arrière-plan.
        On dessine d'abord un voile très léger pour assombrir un peu,
        puis le cadre centré avec le contenu.
        """
        # Voile léger (laisse voir le décor derrière)
        voile = pygame.Surface((w, h), pygame.SRCALPHA)
        voile.fill((0, 0, 0, 100))
        surf.blit(voile, (0, 0))

        # Dimensions du panneau — s'adapte au texte le plus large
        nb_options = len(self.options)
        max_opt_w  = max(
            (self._police_option.size(f" ◆  {o}")[0] for o in self.options),
            default=200
        ) + 60
        if self.title:
            max_opt_w = max(max_opt_w, self._police_titre.size(self.title)[0] + 60)
        panneau_w  = max(300, min(max_opt_w, w - 60))
        panneau_h  = 50 + nb_options * 45 + (80 if self.title else 20)

        px = (w - panneau_w) // 2 + self.offset_x
        py = (h - panneau_h) // 2 + self.offset_y

        # Fond du panneau
        panneau = pygame.Surface((panneau_w, panneau_h), pygame.SRCALPHA)
        panneau.fill((10, 10, 22, 210))
        surf.blit(panneau, (px, py))

        # Double bordure (extérieure + intérieure fine)
        pygame.draw.rect(surf, (110, 90, 200), (px, py, panneau_w, panneau_h), 1)
        pygame.draw.rect(surf, (50, 40, 90),   (px + 3, py + 3, panneau_w - 6, panneau_h - 6), 1)

        y_courant = py + 18

        # Titre du panneau — centré dans le panneau (pas dans l'écran entier)
        centre_x = px + panneau_w // 2
        if self.title:
            t = self._police_titre.render(self.title, True, (190, 170, 255))
            surf.blit(t, (centre_x - t.get_width() // 2, y_courant))
            y_courant += 58

            # Ligne sous le titre
            pygame.draw.line(surf, (70, 55, 140),
                             (px + 20, y_courant - 6),
                             (px + panneau_w - 20, y_courant - 6), 1)

        # Options — centrées dans le panneau
        for i, option in enumerate(self.options):
            if i == self.selection:
                couleur    = (255, 215, 70)
                indicateur = "◆"
            else:
                couleur    = (150, 135, 200)
                indicateur = " "

            opt_surf = self._police_option.render(f" {indicateur}  {option}", True, couleur)
            surf.blit(opt_surf, (centre_x - opt_surf.get_width() // 2, y_courant + i * 42))
