# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Une luciole (petite lumière qui flotte autour du joueur)
# ─────────────────────────────────────────────────────────────────────────────
#
#  À QUOI SERT CE FICHIER ?
#  ------------------------
#  Définit UNE SEULE luciole : un petit point lumineux chaud (jaune/orangé)
#  qui FLOTTE autour du joueur sur une orbite molle. Pas de corps, pas
#  d'yeux, pas de bouche — JUSTE de la lumière. Comme les lucioles dans
#  le fond d'écran du jeu.
#
#  POURQUOI REMPLACER LES "FANTÔMES" PAR DES LUCIOLES ?
#  ----------------------------------------------------
#  Avant, on avait des compagnons (entities/compagnon.py) qui marchaient
#  vers le joueur avec une IA "suit / court / pause". Problèmes :
#       - quand le joueur se collait à un mur, le compagnon essayait de
#         garder sa distance → bug visuel (il rebondissait sur le mur).
#       - graphiquement (blob blanc + yeux + bouche) c'était laid.
#
#  Solution : une luciole NE MARCHE PAS, elle FLOTTE. Elle ignore les murs
#  (pas de collision). C'est juste une lumière. Du coup :
#       - plus de bug de collision (elle traverse les murs, c'est normal)
#       - rendu cohérent avec l'esthétique "ENTRE-DEUX"
#
#  La GESTION DU GROUPE de lucioles (combien il y en a, rappel dans la
#  cape avec [C], effet sur la jauge de peur) est dans :
#       systems/compagnons.py   →  classe CompagnonGroup
#
#  COMPATIBILITÉ AVEC L'ANCIEN CODE
#  --------------------------------
#  Cette classe expose EXACTEMENT la même API que l'ancienne classe
#  Compagnon : __init__(x, y, idx), update(dt, joueur), draw(surf, camera,
#  joueur), distance_au_joueur(joueur), et les mêmes attributs publics
#  (x, y, vx, vy, dans_cape, visibilite, etat). Du coup CompagnonGroup
#  fonctionne sans modification de sa logique : on swap juste l'import.
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  systems/compagnons.py crée une Luciole par "slot" demandé dans
#  game_config.json (clé "nb_compagnons") :
#       self.compagnons.append(Luciole(x, y, idx=i))
#  puis chaque frame :
#       luciole.update(dt, joueur)
#       luciole.draw(surf, camera, joueur)
#
#  JE VEUX MODIFIER QUOI ?
#  -----------------------
#     - Couleur (jaune chaud → vert blafard ?)  → CONSTANTE COULEUR_LUCIOLE
#     - Rayon de l'orbite                       → CONSTANTES RAYON_ORBITE_*
#     - Vitesse de flottement                   → CONSTANTES VITESSE_*
#     - Taille du halo lumineux                 → RAYON_HALO_BASE
#     - Durée de l'animation de cape            → DUREE_ANIM_CAPE
#
#  Petit lexique :
#     - orbite      = trajectoire circulaire (ou elliptique) autour d'un
#                     centre. Ici la luciole tourne autour du joueur.
#     - phase       = "où elle en est dans son orbite", angle entre 0 et 2π.
#                     Initialisée au hasard pour que toutes les lucioles ne
#                     soient pas alignées (sinon on verrait clairement la
#                     copie).
#     - SRCALPHA    = mode pygame qui permet la transparence par pixel
#                     (sans ça, un cercle "alpha 80" serait dessiné comme
#                     un cercle plein opaque).
#     - lerp        = "interpolation linéaire" — mélanger A et B selon un
#                     facteur t ∈ [0,1]. Sert ici à faire rentrer la luciole
#                     dans le joueur quand on la rappelle dans la cape.
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D1]  pygame.Surface          — petite feuille pour dessiner le halo
#     [D2]  SRCALPHA                — transparence du halo
#     [D10] dt                      — temps écoulé depuis la frame précédente
#     [D11] math.hypot              — distance entre 2 points
#     [D12] math.sin / math.cos     — orbite + pulsation
#     [D13] Interpolation linéaire  — fondu position luciole ↔ joueur
#     [D20] Caméra                  — coordonnées écran = monde - offset
#
# ─────────────────────────────────────────────────────────────────────────────

import math
import random
import pygame


# ═════════════════════════════════════════════════════════════════════════════
#  RÉGLAGES (faciles à toucher pour changer le rendu)
# ═════════════════════════════════════════════════════════════════════════════

# Couleur de base d'une luciole : jaune-blanc chaud (R, G, B).
# Variantes essayées :
#     (255, 220, 140)  → jaune chaud "feu de camp"
#     (180, 255, 180)  → vert blafard "marais"
#     (255, 240, 200)  → blanc chaud "phare doux"
COULEUR_LUCIOLE = (255, 230, 160)

# Rayon de l'orbite autour du joueur (en pixels).
# La luciole tourne autour du joueur à une distance variant entre ces deux
# bornes (chaque luciole tire son rayon au hasard à la création).
RAYON_ORBITE_MIN = 35
RAYON_ORBITE_MAX = 70

# Vitesse angulaire (radians/seconde) — vitesse à laquelle la luciole
# tourne autour du joueur. Plus c'est grand, plus elle file.
# 0.6 rad/s ≈ un tour complet en ~10 secondes.
VITESSE_ORBITE_MIN = 0.4
VITESSE_ORBITE_MAX = 0.9

# Amplitude de l'oscillation verticale (en plus de l'orbite) — donne
# l'impression qu'elle "flotte" en plus de tourner.
AMPLITUDE_FLOTTEMENT = 6

# Rayon (en pixels) du halo lumineux dessiné. Plus c'est grand, plus la
# luciole est "imposante" visuellement. Pour de toutes petites lucioles,
# baisser à 8.
RAYON_HALO_BASE = 12

# Durée (s) de l'animation d'entrée/sortie de la cape (rappel par [C]).
DUREE_ANIM_CAPE = 0.35


# ═════════════════════════════════════════════════════════════════════════════
#  LA CLASSE LUCIOLE
# ═════════════════════════════════════════════════════════════════════════════

class Luciole:
    """Une petite lumière qui flotte en orbite autour du joueur.

    Pas de collision avec les murs, pas de comportement complexe : la
    luciole ne fait que tourner doucement autour du joueur en pulsant.
    """

    # ─────────────────────────────────────────────────────────────────────────
    #  1. CONSTRUCTION
    # ─────────────────────────────────────────────────────────────────────────

    def __init__(self, x, y, idx=0):
        """Crée une luciole à la position (x, y).

        idx = numéro dans le groupe (sert à étaler les phases initiales
        des lucioles sur le cercle d'orbite, pour qu'elles ne partent pas
        toutes au même endroit)."""
        self.idx = idx

        # Position courante (float pour des mouvements fluides).
        self.x = float(x)
        self.y = float(y)

        # Vitesse — exposée pour compat avec l'ancienne API Compagnon.
        # On ne s'en sert pas vraiment (la luciole n'a pas de "vélocité"
        # logique), mais certains anciens codes pouvaient la lire.
        self.vx = 0.0
        self.vy = 0.0

        # ── État cape (compat) ───────────────────────────────────────────
        # dans_cape  = ce qu'on VEUT (True = rappelée, False = sortie)
        # visibilite = ce qu'on VOIT (1 = entièrement visible, 0 = cachée)
        self.dans_cape = False
        self.visibilite = 1.0

        # État textuel exposé pour compat (ancien code testait c.etat).
        # Toujours "suit" : la luciole n'a pas de machine à états réelle.
        self.etat = "suit"

        # ── Paramètres uniques de cette luciole ──────────────────────────
        # On donne à chaque luciole son propre rayon, sa vitesse et sa
        # phase de départ → l'essaim a l'air vivant, pas répétitif.

        # Phase de départ : étalée selon idx pour que les premières lucioles
        # soient régulièrement espacées sur le cercle, plus petite variation
        # aléatoire pour casser la symétrie.
        #   2π / 5 ≈ 1.26 → 5 lucioles régulièrement réparties
        # On part du principe qu'on aura rarement plus de ~5 lucioles ; au-
        # delà ça commence à se chevaucher mais pas grave.
        self.phase = (idx * (2 * math.pi / 5)) + random.uniform(-0.3, 0.3)

        # Rayon d'orbite et vitesse angulaire : un peu différents par luciole.
        self.rayon_orbite = random.uniform(RAYON_ORBITE_MIN, RAYON_ORBITE_MAX)
        self.vitesse_orbite = random.uniform(VITESSE_ORBITE_MIN, VITESSE_ORBITE_MAX)

        # Compteur pour le flottement vertical et la pulsation du halo.
        # Phase aléatoire pour qu'elles ne pulsent pas en rythme.
        self.t_flottement = random.uniform(0.0, 6.28)

    # ─────────────────────────────────────────────────────────────────────────
    #  2. UPDATE (appelé chaque frame)
    # ─────────────────────────────────────────────────────────────────────────
    #
    #  Appelé par CompagnonGroup.update() depuis core/game.py.
    #  On calcule la nouvelle position sur l'orbite — pas de collision,
    #  la luciole traverse les murs (intentionnel).

    def update(self, dt, joueur):
        """Met à jour la position de la luciole sur son orbite."""

        # ── 1) Animation de visibilité (fondu cape) ─────────────────────
        # Même mécanisme que l'ancienne classe Compagnon : on tire
        # visibilite vers 0 (rappelée) ou vers 1 (sortie) à vitesse
        # 1 / DUREE_ANIM_CAPE par seconde.
        vitesse_anim = 1.0 / DUREE_ANIM_CAPE
        if self.dans_cape:
            self.visibilite -= vitesse_anim * dt
            if self.visibilite < 0.0:
                self.visibilite = 0.0
        else:
            self.visibilite += vitesse_anim * dt
            if self.visibilite > 1.0:
                self.visibilite = 1.0

        # ── 2) Cas particulier : quasi totalement dans la cape ──────────
        # Pas la peine de calculer l'orbite, on la colle au joueur.
        if self.dans_cape and self.visibilite <= 0.01:
            self.x = float(joueur.rect.centerx)
            self.y = float(joueur.rect.centery)
            return

        # ── 3) Avance la phase et le compteur de flottement ─────────────
        self.phase += self.vitesse_orbite * dt
        self.t_flottement += dt * 2.0   # pulsation halo + flottement

        # ── 4) Position cible sur l'orbite autour du joueur ─────────────
        # cos / sin [D12] → coordonnées sur un cercle de rayon donné.
        # On centre l'orbite légèrement au-dessus du joueur (épaule)
        # plutôt que sur ses pieds, pour que les lucioles "encadrent"
        # le personnage.
        centre_x = joueur.rect.centerx
        centre_y = joueur.rect.centery - 10

        cible_x = centre_x + math.cos(self.phase) * self.rayon_orbite
        cible_y = centre_y + math.sin(self.phase) * (self.rayon_orbite * 0.5)
        # NB : on multiplie sin(...) par 0.5 → orbite ELLIPTIQUE aplatie
        # (plus large que haute), ça donne un mouvement plus naturel
        # quand vu de côté (jeu en 2D vue latérale).

        # ── 5) Petit flottement supplémentaire en Y (sinusoïdal) ────────
        flottement = math.sin(self.t_flottement) * AMPLITUDE_FLOTTEMENT
        cible_y += flottement

        # ── 6) Lissage : on tend vers la cible plutôt que d'y être pile ─
        # Ça donne un mouvement "mou" — la luciole ne file pas instan-
        # tanément à sa position théorique, elle y tend doucement.
        # Facteur 5.0 : plus c'est haut, plus elle suit vite (à 60 fps,
        # 5.0 * dt ≈ 0.083 → 8% de la distance comblée par frame).
        facteur_lissage = 5.0
        self.x += (cible_x - self.x) * facteur_lissage * dt
        self.y += (cible_y - self.y) * facteur_lissage * dt

    # ─────────────────────────────────────────────────────────────────────────
    #  3. DISTANCE AU JOUEUR (pour la jauge de peur)
    # ─────────────────────────────────────────────────────────────────────────
    #
    #  Utilisé par CompagnonGroup.affecter_peur() : si la luciole est
    #  proche du joueur, elle réduit la peur.
    #  Comportement identique à l'ancienne classe Compagnon.

    def distance_au_joueur(self, joueur):
        """Renvoie la distance (px) entre la luciole et le joueur.

        Si la luciole est totalement dans la cape, on considère qu'elle
        est "avec" le joueur (distance 0) — sinon elle compterait comme
        loin pendant l'animation de fondu."""

        if self.dans_cape and self.visibilite <= 0.01:
            return 0.0
        dx = joueur.rect.centerx - self.x
        dy = joueur.rect.centery - self.y
        return math.hypot(dx, dy)   # [D11]

    # ─────────────────────────────────────────────────────────────────────────
    #  4. RENDU
    # ─────────────────────────────────────────────────────────────────────────
    #
    #  Appelé chaque frame par CompagnonGroup.draw().
    #  Pendant l'animation de cape, on interpole [D13] la position entre
    #  la luciole et le joueur (elle "rentre" dans le joueur en
    #  rétrécissant et en s'estompant).

    def draw(self, surf, camera, joueur):
        """Dessine la luciole : juste un halo lumineux, rien d'autre."""

        # Totalement invisible → rien à faire (économie).
        if self.visibilite <= 0.01:
            return

        # ── Position à l'écran (avec interpolation cape) ────────────────
        # t = 1 → vraie position de la luciole
        # t = 0 → position du joueur
        # entre les deux → mélange (la luciole "fond" dans le joueur).
        t = self.visibilite
        pos_x = (1 - t) * joueur.rect.centerx + t * self.x
        pos_y = (1 - t) * joueur.rect.centery + t * self.y

        # Coordonnées écran (on retire l'offset de la caméra [D20]).
        sx = int(pos_x - camera.offset_x)
        sy = int(pos_y - camera.offset_y)

        # ── Pulsation du halo (sinus → respiration douce) ───────────────
        # Oscille entre 0.7 et 1.0 → halo qui "respire".
        pulsation = 0.85 + 0.15 * math.sin(self.t_flottement * 1.3)

        # Rayon du halo, modulé par la visibilité ET la pulsation.
        rayon = int(RAYON_HALO_BASE * self.visibilite * pulsation)
        if rayon < 2:
            return

        # ── Dessin du halo : cercles concentriques sur Surface SRCALPHA ─
        # On dessine sur une petite Surface séparée [D1] avec SRCALPHA [D2]
        # pour avoir une vraie transparence par pixel. Sinon les cercles
        # transparents s'empileraient comme des cercles opaques.
        taille = rayon * 2
        halo = pygame.Surface((taille, taille), pygame.SRCALPHA)

        # On dessine plusieurs cercles concentriques, du plus grand
        # (transparent) au plus petit (opaque). L'effet final = un point
        # lumineux qui irradie. range(rayon, 0, -2) = rayon, rayon-2, …
        r_couleur, g_couleur, b_couleur = COULEUR_LUCIOLE
        for r in range(rayon, 0, -2):
            # Plus le cercle est petit (proche du centre), plus il est opaque.
            # Formule : alpha = (1 - r/rayon)² × 220
            # Le carré ((1-x)²) creuse le centre — la lumière paraît plus
            # vive au cœur et fond très progressivement vers l'extérieur.
            facteur = 1.0 - (r / rayon)
            alpha = int(facteur * facteur * 220)
            couleur = (r_couleur, g_couleur, b_couleur, alpha)
            pygame.draw.circle(halo, couleur, (rayon, rayon), r)

        # On colle le halo à l'écran, centré sur la position.
        # NOTE : surf.blit utilise par défaut le mode BLEND_ALPHA correct
        # pour SRCALPHA. Si on voulait un effet "addition de lumière"
        # plus saturé (plusieurs lucioles = blanc lumineux), il faudrait
        # passer special_flags=pygame.BLEND_ADD à blit. Pour l'instant
        # on reste sur le mode normal (plus doux, moins criard).
        surf.blit(halo, (sx - rayon, sy - rayon))
