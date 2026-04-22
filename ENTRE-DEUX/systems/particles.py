# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Système de particules
# ─────────────────────────────────────────────────────────────────────────────
#
#  À QUOI SERT CE FICHIER ?
#  ------------------------
#  Quand le joueur saute, atterrit, dash, ou frappe un ennemi, on a envie
#  qu'il se passe quelque chose à l'écran : un petit nuage de poussière, des
#  étincelles, une traînée bleutée derrière le dash. Sans ça, le jeu donne
#  l'impression d'être en carton.
#
#  Une particule = un petit point coloré qui :
#       1) apparaît à un endroit précis (x, y),
#       2) a une vitesse (vx, vy) et subit (ou pas) la gravité,
#       3) vit pendant un certain temps (life),
#       4) puis disparaît, parfois en s'éteignant doucement (fade).
#
#  Ce fichier offre UNE classe : ParticleSystem.
#  Tu en crées UNE pour tout le jeu, tu lui demandes des effets, et elle
#  s'occupe de tout (mise à jour + dessin).
#
#  EXEMPLE CONCRET
#  ---------------
#       particles = ParticleSystem()                          # une seule fois
#       ...
#       # Le joueur atterrit → poussière jaune sous ses pieds :
#       particles.burst(joueur.rect.centerx,
#                       joueur.rect.bottom,
#                       nb=10,
#                       couleur=(230, 220, 180))
#       ...
#       # Chaque frame :
#       particles.update(dt)
#       particles.draw(surface_monde, camera)
#
#  Au final, 10 petits points jaunes partent vers le haut, tombent à cause
#  de la gravité, deviennent transparents, puis disparaissent.
#
#  POURQUOI DES dict AU LIEU D'UNE CLASSE Particle ?
#  -------------------------------------------------
#  On pourrait écrire `class Particle:` avec 10 attributs. Mais avec un dict
#  on voit TOUT le contenu d'une particule en un coup d'œil, et on n'a pas
#  20 lignes de boilerplate (`__init__`, etc.). Pour 8 champs simples qu'on
#  ne réutilise nulle part ailleurs, c'est plus court et plus lisible.
#
#  Petit lexique :
#     - particule  = un petit élément visuel éphémère (durée < 1s en général).
#     - burst      = "explosion" → on crée plusieurs particules d'un coup.
#     - trail      = "traînée"   → une seule particule qui ne bouge pas et
#                                  s'éteint doucement (sert à marquer un
#                                  passage, ex : derrière le dash).
#     - life       = combien de secondes il reste à vivre à la particule.
#                    À chaque frame on lui retire `dt`. À 0 → elle disparaît.
#     - fade       = "fondu" → la particule devient transparente avant de
#                    mourir, au lieu de disparaître brutalement.
#     - alpha      = transparence (0 = invisible, 255 = totalement opaque).
#     - dt         = "delta time" = temps écoulé depuis la frame précédente,
#                    en secondes (souvent ~0.016 s à 60 fps).
#     - SRCALPHA   = drapeau pygame qui dit "cette surface a un canal de
#                    transparence". Sans lui, pas de fade possible.
#
#  POURQUOI UN max_particles = 400 ?
#  ---------------------------------
#  Si on laissait spammer sans limite, un effet abusif pourrait remplir
#  l'écran de 50 000 points et faire chuter le framerate à 5 fps. Avec
#  un plafond, on refuse les nouvelles particules dès qu'on est plein —
#  visuellement on ne voit pas la différence, mais on garde 60 fps.
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  core/game.py crée le ParticleSystem et appelle update() + draw() chaque
#  frame. Le joueur, les ennemis, et certains événements appellent burst()
#  ou trail() pour créer les effets.
#
#  JE VEUX MODIFIER QUOI ?
#  -----------------------
#     - Une particule plus grosse / plus petite → paramètre `taille` de burst()
#     - Plus de particules par effet              → paramètre `nb`
#     - Particules qui ne tombent pas             → paramètre `gravity=0`
#     - Couleur                                    → paramètre `couleur`
#     - Plafond de perfs                           → max_particles dans __init__
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D8]   dt              — temps inter-frames pour une physique stable
#     [D14]  pygame.Surface  — petit canvas où on dessine, puis qu'on blit
#     [D17]  alpha           — transparence par pixel (avec SRCALPHA)
#
# ─────────────────────────────────────────────────────────────────────────────

import random
import pygame


# ═════════════════════════════════════════════════════════════════════════════
#  CLASSE ParticleSystem
# ═════════════════════════════════════════════════════════════════════════════

class ParticleSystem:

    def __init__(self, max_particles=400):
        # Liste plate de toutes les particules vivantes.
        # Une particule = un dict (voir _make_particle() plus bas).
        self._particles    = []
        self.max_particles = max_particles

    # ─────────────────────────────────────────────────────────────────────────
    #  1. ÉMISSION (créer des particules)
    # ─────────────────────────────────────────────────────────────────────────

    def burst(self, x, y, nb=8,
              couleur=(255, 255, 200),
              vx_range=(-120, 120),
              vy_range=(-220, -40),
              gravity=600,
              taille=(1, 3),
              duree=(0.3, 0.7),
              fade=True):
        """Crée `nb` particules à (x, y), avec vitesses & durées aléatoires.

        Chaque paramètre `xxx_range = (mini, maxi)` veut dire :
        "tire un nombre aléatoire entre mini et maxi pour CHAQUE particule".
        C'est ce qui donne l'effet "explosion qui part dans tous les sens"
        plutôt que "10 particules identiques qui se chevauchent".

        EXEMPLE
        -------
            burst(100, 200, nb=15,
                  couleur=(255, 100, 50),     # orange
                  vy_range=(-300, -100))      # vont fort vers le haut
            → 15 particules orange qui s'élèvent puis retombent.
        """
        for _ in range(nb):
            # Plein → on refuse silencieusement (pas d'erreur, juste rien).
            if len(self._particles) >= self.max_particles:
                return

            life = random.uniform(*duree)
            self._particles.append({
                "x":        float(x),
                "y":        float(y),
                "vx":       random.uniform(*vx_range),
                "vy":       random.uniform(*vy_range),
                "g":        gravity,
                "size":     random.uniform(*taille),
                "life":     life,        # temps restant
                "max_life": life,        # temps total (sert au calcul du fade)
                "color":    couleur,
                "fade":     fade,
            })

    def trail(self, x, y, couleur=(180, 220, 255)):
        """Une seule particule fixe qui s'éteint doucement (~0.25s).

        Utile pour marquer un passage : on en émet une à chaque frame du
        dash, et ça fait une jolie traînée bleutée derrière le joueur.
        """
        if len(self._particles) >= self.max_particles:
            return
        self._particles.append({
            "x": float(x), "y": float(y),
            "vx": 0, "vy": 0, "g": 0,             # ne bouge pas
            "size": random.uniform(2.0, 3.5),
            "life": 0.25, "max_life": 0.25,
            "color": couleur, "fade": True,
        })

    # ─────────────────────────────────────────────────────────────────────────
    #  2. MISE À JOUR (chaque frame, avant draw())
    # ─────────────────────────────────────────────────────────────────────────

    def update(self, dt):
        """Avance le temps : chaque particule bouge un peu, vieillit un peu.

        ASTUCE : on RECONSTRUIT une nouvelle liste `alive` au lieu de
        supprimer dans `_particles` pendant qu'on l'itère. C'est plus
        simple et c'est en pratique plus rapide en Python pour des
        listes de quelques centaines d'éléments.
        """
        alive = []
        for p in self._particles:
            p["life"] -= dt
            if p["life"] <= 0:
                continue                          # morte → on l'oublie

            # Physique simple : v += g·dt   puis   pos += v·dt
            # (intégration d'Euler — bourrin mais largement suffisant ici)
            p["vy"] += p["g"]  * dt
            p["x"]  += p["vx"] * dt
            p["y"]  += p["vy"] * dt
            alive.append(p)
        self._particles = alive

    # ─────────────────────────────────────────────────────────────────────────
    #  3. RENDU
    # ─────────────────────────────────────────────────────────────────────────

    def draw(self, surf, camera):
        """Dessine toutes les particules sur `surf`, vues depuis la caméra."""
        for p in self._particles:
            # Conversion coords MONDE → coords ÉCRAN (la caméra fait le reste).
            sx   = int(p["x"] - camera.offset_x)
            sy   = int(p["y"] - camera.offset_y)
            size = max(1, int(p["size"]))

            if p["fade"]:
                # Fondu : alpha = ratio de vie restante (1.0 → 0.0).
                # Quand life vaut max_life → 100% opaque.
                # Quand life arrive à 0    →   0% opaque.
                a = int(255 * (p["life"] / p["max_life"]))
                color = (*p["color"], max(0, min(255, a)))

                # Pour bénéficier de l'alpha, il FAUT une surface SRCALPHA :
                # on dessine le cercle dessus, puis on blit.
                tmp = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(tmp, color, (size, size), size)
                surf.blit(tmp, (sx - size, sy - size))
            else:
                # Pas de fade → on peut dessiner direct sur surf, c'est plus rapide.
                pygame.draw.circle(surf, p["color"], (sx, sy), size)

    # ─────────────────────────────────────────────────────────────────────────
    #  4. UTILITAIRES
    # ─────────────────────────────────────────────────────────────────────────

    def clear(self):
        """Vide tout (ex : changement de carte, on ne veut pas garder
        les particules de la salle précédente)."""
        self._particles.clear()

    def __len__(self):
        """Permet d'écrire `len(particles)` au lieu de `len(particles._particles)`.
        Pratique pour debug : `print(len(particles))` affiche le compteur."""
        return len(self._particles)
