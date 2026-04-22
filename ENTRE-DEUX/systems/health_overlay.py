# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Filtre visuel "tu as mal"
# ─────────────────────────────────────────────────────────────────────────────
#
#  À QUOI SERT CE FICHIER ?
#  ------------------------
#  Quand le joueur perd des PV, on veut que ÇA SE VOIE. Pas juste un chiffre
#  qui descend dans le HUD : on veut que la sensation de danger se ressente.
#
#  Donc ce module ajoute par-dessus l'image du jeu :
#       1) Une vignette ROUGE sur les bords (plus on est blessé, plus
#          c'est rouge et opaque).
#       2) Un voile NOIR global qui apparaît quand on tombe sous 30 % de PV
#          (l'écran s'assombrit, on sent que ça va mal).
#       3) Une PULSATION cardiaque quand HP = 1 (bat-bat, bat-bat...) qui
#          fait osciller l'intensité de la vignette → pic de tension finale.
#
#  Tout ça est rendu APRÈS le monde mais AVANT le HUD. Comme ça, les
#  jauges (vie, etc.) restent lisibles par-dessus l'effet.
#
#  EXEMPLE CONCRET (4 PV max)
#  --------------------------
#       hp = 4 (100 %)  → ratio=1.00 → rien ne s'affiche.
#       hp = 3 ( 75 %)  → ratio=0.75 → encore au-dessus de 60 %, rien.
#       hp = 2 ( 50 %)  → ratio=0.50 → vignette rouge légère.
#       hp = 1 ( 25 %)  → ratio=0.25 → vignette rouge VIVE
#                                      + voile sombre (ratio < 30 %)
#                                      + pulsation cardiaque (HP == 1).
#       hp = 0          → game over (on n'arrive même pas ici).
#
#  Petit lexique :
#     - vignette   = effet visuel où les bords sont plus sombres / colorés
#                    que le centre. Très utilisé au cinéma / en photo pour
#                    attirer l'œil au milieu de l'image.
#     - voile      = un grand carré semi-transparent posé sur tout l'écran.
#                    Ici, voile noir = on assombrit. Voile rouge = on rougit.
#     - alpha      = transparence (0 = invisible, 255 = totalement opaque).
#     - ratio      = un nombre entre 0 et 1 (0 = mort, 1 = pleine vie).
#                    On préfère ça à des PV bruts, parce que c'est
#                    indépendant du nombre de PV max (marche pour 3 PV
#                    comme pour 100 PV).
#     - cache      = "garder en mémoire un calcul lourd pour ne pas le
#                    refaire à chaque frame". Ici on cache la VIGNETTE.
#     - pulsation  = oscillation régulière (sin) qui donne l'impression
#                    d'un battement de cœur.
#     - SRCALPHA   = drapeau pygame "cette surface a un canal de transparence
#                    PAR PIXEL". Indispensable pour faire un dégradé propre.
#     - hypot      = math.hypot(a, b) = √(a² + b²) = la diagonale d'un
#                    rectangle a × b. Sert à mesurer du centre au coin.
#
#  POURQUOI ON RECRÉE LA VIGNETTE UNE FOIS, PAS À CHAQUE FRAME ?
#  -------------------------------------------------------------
#  Dessiner 24 cercles de plusieurs centaines de pixels de rayon, c'est
#  COÛTEUX. Mais une fois qu'on l'a, l'image est la même tant que la
#  fenêtre ne change pas de taille. Donc on la calcule UNE SEULE FOIS
#  (à la première frame, ou si la fenêtre change de taille), puis à
#  chaque frame on se contente de moduler son alpha → quasi-gratuit.
#
#  POURQUOI 24 CERCLES CONCENTRIQUES (pas un dégradé propre) ?
#  -----------------------------------------------------------
#  Parce qu'un vrai dégradé radial pixel par pixel demanderait numpy
#  (ou une boucle Python lente). Avec 24 cercles on obtient un effet
#  visuel quasi-identique, sans dépendance, et lisible par un élève.
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  core/game.py : self.health_overlay = HealthOverlay()
#                 self.health_overlay.update(dt)
#                 self.health_overlay.draw(screen, self.joueur)
#
#  JE VEUX MODIFIER QUOI ?
#  -----------------------
#     - L'effet apparaît plus tôt / plus tard      → SEUIL_FILTRE
#     - L'écran s'assombrit plus tôt / plus tard   → SEUIL_DARK
#     - Couleur de la vignette                     → COULEUR_ROUGE
#     - Vignette plus ou moins intense au max     → ALPHA_VIGNETTE_MAX
#     - Vitesse du battement cardiaque             → coefficient 6.0 dans
#                                                    sin(self._pulse_t * 6.0)
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D14]  pygame.Surface  — image hors-écran qu'on construit puis qu'on blit
#     [D17]  alpha           — transparence par pixel ou par surface
#     [D22]  ratio           — un float dans [0, 1] indépendant des unités
#
# ─────────────────────────────────────────────────────────────────────────────

import math
import pygame


# ═════════════════════════════════════════════════════════════════════════════
#  1. RÉGLAGES (les constantes qu'on touche pour équilibrer)
# ═════════════════════════════════════════════════════════════════════════════

# Sous quel ratio (hp / max_hp) on commence à voir la vignette rouge.
# 0.60 = "à partir de 60 % de PV ou moins, ça commence à rougir".
SEUIL_FILTRE   = 0.60

# Sous quel ratio on AJOUTE le voile sombre par-dessus.
# 0.30 = "à 30 % de PV ou moins, l'écran s'assombrit aussi".
SEUIL_DARK     = 0.30

# Couleurs (RGB sans alpha — l'alpha est calculé dynamiquement).
COULEUR_ROUGE  = (180,  20,  30)
COULEUR_NOIR   = (  0,   0,   0)

# Opacités MAXIMALES (atteintes quand le joueur est au plus mal).
# 255 = totalement opaque. 0 = totalement transparent.
ALPHA_VIGNETTE_MAX = 180   # vignette rouge à 1 PV
ALPHA_DARK_MAX     = 90    # voile sombre   à 1 PV


# ═════════════════════════════════════════════════════════════════════════════
#  2. LA CLASSE
# ═════════════════════════════════════════════════════════════════════════════

class HealthOverlay:
    """Lit hp / max_hp depuis le joueur et rend la vignette rouge + voile."""

    def __init__(self):
        # Cache de la vignette : on stocke la SURFACE déjà dessinée + la
        # taille pour laquelle on l'a calculée. Si la fenêtre est
        # redimensionnée, on regénère.
        self._cache_size = None    # tuple (w, h) — taille actuellement cachée
        self._vignette   = None    # pygame.Surface (None tant que pas générée)

        # Horloge interne pour la pulsation cardiaque (HP=1).
        # Augmente à chaque update(), sert d'argument au sin().
        self._pulse_t    = 0.0

    # ─────────────────────────────────────────────────────────────────────────
    #  MISE À JOUR (appelée chaque frame, juste pour la pulsation HP=1)
    # ─────────────────────────────────────────────────────────────────────────

    def update(self, dt):
        # On accumule le temps écoulé. Plus ce nombre grossit, plus le sin
        # oscille loin → effet "bat-bat" continu.
        self._pulse_t += dt

    # ─────────────────────────────────────────────────────────────────────────
    #  RENDU (appelé chaque frame, après le monde, avant le HUD)
    # ─────────────────────────────────────────────────────────────────────────

    def draw(self, screen, joueur):
        # Garde-fous : pas de joueur, ou max_hp invalide → on ne fait rien
        # (évite une division par zéro juste après).
        if joueur is None or joueur.max_hp <= 0:
            return

        ratio = joueur.hp / joueur.max_hp
        if ratio >= SEUIL_FILTRE:
            return                         # tout va bien → pas d'overlay

        # On s'assure que la vignette existe à la bonne taille.
        w, h = screen.get_size()
        self._ensure_vignette(w, h)

        # ── Intensité du rouge (linéaire de SEUIL_FILTRE → 0) ────────────────
        # ratio = 0.60 → intensite = 0.0 (juste à la limite, invisible)
        # ratio = 0.30 → intensite = 0.5 (mi-chemin)
        # ratio = 0.00 → intensite = 1.0 (max)
        intensite = max(0.0, min(1.0, (SEUIL_FILTRE - ratio) / SEUIL_FILTRE))

        # ── Pulsation cardiaque si HP = 1 ────────────────────────────────────
        # sin(t*6) oscille entre -1 et +1 à raison d'environ 1 cycle par
        # seconde. On le ramène entre 0 et 1 (0.5 + 0.5*sin), puis on
        # ajoute jusqu'à +0.15 d'intensité. Résultat : la vignette pulse.
        if joueur.hp == 1:
            pulse     = 0.5 + 0.5 * math.sin(self._pulse_t * 6.0)
            intensite = min(1.0, intensite + 0.15 * pulse)

        # ── Application de la vignette rouge ─────────────────────────────────
        # On ne REDESSINE PAS la vignette, on lui change juste son alpha global.
        # set_alpha = "rends la surface entière X fois moins opaque qu'elle ne
        # l'est dans ses pixels". Coût quasi-nul.
        alpha = int(ALPHA_VIGNETTE_MAX * intensite)
        if alpha > 0:
            self._vignette.set_alpha(alpha)
            screen.blit(self._vignette, (0, 0))

        # ── Voile noir global (uniquement sous SEUIL_DARK) ───────────────────
        # On crée à chaque frame parce que c'est juste un fill noir : c'est
        # beaucoup moins coûteux que la vignette (pas de cercles à dessiner).
        if ratio < SEUIL_DARK:
            dark_intensite = (SEUIL_DARK - ratio) / SEUIL_DARK   # 0 → 1
            dark_alpha     = int(ALPHA_DARK_MAX * dark_intensite)
            if dark_alpha > 0:
                voile = pygame.Surface((w, h))
                voile.fill(COULEUR_NOIR)
                voile.set_alpha(dark_alpha)
                screen.blit(voile, (0, 0))

    # ─────────────────────────────────────────────────────────────────────────
    #  CONSTRUCTION DE LA VIGNETTE (caché : ne se fait qu'une fois)
    # ─────────────────────────────────────────────────────────────────────────

    def _ensure_vignette(self, w, h):
        """Génère (une seule fois) une surface rouge ~transparente au centre,
        ~opaque sur les bords, façon vignette de blessure.

        Si la vignette est déjà à la bonne taille → on sort tout de suite.
        Sinon (première fois, ou fenêtre redimensionnée) → on regénère.
        """
        # Cache déjà à jour ?
        if self._cache_size == (w, h) and self._vignette is not None:
            return
        self._cache_size = (w, h)

        # Surface vide totalement transparente (SRCALPHA → alpha par pixel).
        surf   = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2

        # Diagonale du quart d'écran (centre → coin) = rayon max utile.
        # math.hypot(cx, cy) = √(cx² + cy²).
        diag   = math.hypot(cx, cy)

        # On dessine 24 cercles concentriques :
        #   - du PLUS GRAND (couvre tout l'écran) → presque transparent
        #   - au PLUS PETIT (juste autour du centre) → opaque
        # En les superposant, l'effet final est une vignette dégradée.
        #
        # Pourquoi pas un vrai dégradé pixel-par-pixel ? Ça demanderait numpy
        # (ou une boucle Python LENTE). 24 cercles c'est largement assez
        # à l'œil et ça reste lisible pour un élève.
        nb_cercles = 24
        for i in range(nb_cercles):
            t      = i / nb_cercles                      # va de 0 à ~1
            rayon  = int(diag * (1.0 - t * 0.55))        # de diag à ~45% diag
            alpha  = int(255 * (t ** 1.6))               # croît vers les bords
            # Le 30 final = épaisseur du trait (cercle creux, pas plein).
            pygame.draw.circle(surf, (*COULEUR_ROUGE, alpha), (cx, cy), rayon, 30)

        self._vignette = surf
