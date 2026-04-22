# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Système d'éclairage
# ─────────────────────────────────────────────────────────────────────────────
#
#  À QUOI SERT CE FICHIER ?
#  ------------------------
#  C'est ce qui rend le jeu SOMBRE par défaut, avec des halos lumineux
#  autour du joueur et des sources de lumière (torches, lanternes, lueurs
#  d'ennemis...). Sans ce système, on verrait toute la map d'un coup et
#  on perdrait toute l'ambiance de "grotte" du jeu.
#
#  IDÉE DE BASE (pas évidente du tout, mais simple une fois comprise) :
#
#       1) On part d'une image NOIRE de la taille de l'écran.
#       2) On ajoute (en blanc) un halo à chaque endroit lumineux :
#          - autour du joueur
#          - à chaque source de lumière de la scène
#       3) On AJOUTE par-dessus une "ambiance" gris-foncé pour que les
#          zones complètement sombres ne soient pas 100% noires.
#       4) On MULTIPLIE cette image (noir + halos blancs) sur le monde :
#                 - là où c'est NOIR  → noir × monde = noir → invisible
#                 - là où c'est BLANC → blanc × monde = monde → visible
#
#  Résultat : on ne voit que les endroits éclairés, le reste fond dans le noir.
#
#  EXEMPLE CONCRET (ce que tu vois)
#  --------------------------------
#       Tu marches dans une grotte. Le joueur a son halo (RAYON_JOUEUR).
#       Tu approches d'une torche (light_type="torch", radius=150).
#       → Les deux halos se SUPERPOSENT (additif), donc autour de la torche
#         tout est bien éclairé. Tu t'éloignes → seul ton halo reste.
#
#  PETIT LEXIQUE
#  -------------
#     - halo            = le cercle de lumière autour d'une source. Ici on
#                         charge des images PNG pré-dessinées (light_*.png)
#                         qui donnent un dégradé "doux" du centre vers
#                         l'extérieur.
#
#     - alpha           = opacité (0 = invisible, 255 = opaque). On l'utilise
#                         pour faire vibrer un halo (flicker = scintillement).
#
#     - flicker         = scintillement d'une lumière (genre torche qui
#                         tremble). On fait varier l'alpha au cours du temps
#                         avec une fonction sinus.
#
#     - cache           = mémoire qui retient un calcul coûteux pour ne pas
#                         le refaire. Ici on cache les surfaces redimensionnées
#                         et modulées (ça évite de re-créer 60 images/s).
#
#     - quantification  = "arrondir à un palier". Si l'alpha varie en continu
#                         (210, 211, 212, …) on aurait des MILLIERS d'entrées
#                         dans le cache. On arrondit au multiple de 8
#                         → seulement ~12 valeurs possibles → cache mini.
#
#     - cull (culling)  = ignorer ce qui est hors écran (économie CPU/GPU).
#                         Si une lumière est à 5000 pixels à droite et qu'on
#                         regarde l'écran d'en bas à gauche, on la SAUTE.
#
#     - BLEND_RGB_ADD   = "additionner les couleurs". (50,50,50) + (100,0,0)
#                         = (150,50,50). Ça SOMME les lumières (deux torches
#                         côte à côte = plus clair). C'est le mode physique
#                         de la lumière — la lumière s'ajoute, ne se remplace.
#
#     - BLEND_RGB_MAX   = "garder le maximum couleur par couleur". On l'utilise
#                         pour fusionner notre noir+halos avec l'AMBIANCE
#                         gris foncé (pour que le noir pur n'existe jamais).
#
#     - BLEND_RGB_MULT  = "multiplier les couleurs" (divisé par 255). Sert à
#                         APPLIQUER notre image lumière sur le monde :
#                         monde × (0,0,0) = noir (caché)
#                         monde × (255,255,255) = monde (visible)
#                         monde × (128,128,128) = monde à 50% (pénombre)
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  core/game.py crée l'instance et l'appelle chaque frame :
#       self.lighting = LightingSystem()
#       self.lighting.update(dt)                                # flicker
#       self.lighting.render(self.screen, self.camera, self.joueur.rect)
#  L'éditeur (world/editor.py) ajoute des lumières via add_light().
#
#  JE VEUX MODIFIER QUOI ?
#  -----------------------
#     - Luminosité d'ambiance     → settings.FOND_ALPHA (plus haut = plus clair)
#     - Halo du joueur            → settings.RAYON_JOUEUR
#     - Une nouvelle texture      → ajoute light_X.png + entrée dans names{}
#     - Vitesse du scintillement  → arg flicker_speed de add_light()
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D5]  pygame.Surface       — surfaces tampons (darkness, ambient)
#     [D8]  blit + special_flags — additive / multiplicative blending
#     [D10] dt                   — phase du scintillement avancée par dt
#
# ─────────────────────────────────────────────────────────────────────────────

import os
import math
import random
import pygame

from settings import FOND_ALPHA, RAYON_JOUEUR


# Dossier des textures de lumière. _BASE_DIR = racine du projet ENTRE-DEUX/.
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_IMG_DIR  = os.path.join(_BASE_DIR, "assets", "images", "lumieres")


class LightingSystem:
    """Gère toutes les lumières d'un niveau et le rendu final assombri."""

    # ═════════════════════════════════════════════════════════════════════════
    #  1. CONSTRUCTION
    # ═════════════════════════════════════════════════════════════════════════

    def __init__(self):
        # Liste de toutes les sources de lumière (sauf le joueur, qui est
        # ajouté à la volée à chaque render).
        self.lights = []

        # Cache des halos redimensionnés.
        # Clé   = (rayon, type)
        # Valeur = pygame.Surface du halo à cette taille
        # → évite de redimensionner la texture à chaque frame.
        self._cache = {}

        # Cache des halos VIBRANTS (avec un alpha modulé).
        # Clé   = (rayon, type, alpha)
        # Valeur = halo de base × alpha
        # → grâce à la quantification dans update(), il y a peu de valeurs
        #   d'alpha distinctes (~12), donc ce cache reste petit.
        self._flick_cache = {}

        # Surfaces tampons recréées seulement quand la taille de l'écran
        # change (ex: passage en plein écran). On les garde en attribut
        # pour ne pas les recréer chaque frame.
        self._darkness    = None     # tampon "noir + halos"
        self._ambient     = None     # voile gris constant
        self._screen_size = (0, 0)   # taille connue (déclencheur de re-création)

    # ═════════════════════════════════════════════════════════════════════════
    #  2. AJOUTER UNE LUMIÈRE (appelée par l'éditeur ou le chargement de map)
    # ═════════════════════════════════════════════════════════════════════════

    def add_light(self, x, y, radius, type="player", flicker=False, flicker_speed=5):
        """Crée une nouvelle source de lumière à la position (x, y).

        type           : "player"/"torch"/"large"/"cool"/"dim"/"background"
                         → choisit la texture de halo (voir _load_textures).
        flicker        : True = la lumière scintille (alpha qui varie).
        flicker_speed  : vitesse du scintillement (rad/s du sinus).
        """
        self.lights.append({
            "x": x, "y": y, "radius": radius,
            "type": type, "flicker": flicker,
            "flicker_speed": flicker_speed,
            # Phase initiale aléatoire → toutes les torches ne scintillent
            # pas en même temps (sinon ce serait artificiel et synchrone).
            "_phase": random.random() * 6.28,    # 6.28 ≈ 2π = un tour complet
            "_alpha": 210,                        # alpha "neutre" de départ
        })

    # ═════════════════════════════════════════════════════════════════════════
    #  3. UPDATE — fait avancer le scintillement (à appeler chaque frame)
    # ═════════════════════════════════════════════════════════════════════════

    def update(self, dt):
        """Avance la phase de chaque lumière qui scintille.

        Pour chaque lumière flicker :
            1) on incrémente sa phase (= avance dans le sinus)
            2) on calcule un alpha basé sur sin(phase) → varie entre 165 et 255
            3) on QUANTIFIE l'alpha à un multiple de 8 (>>3 puis <<3)
               → moins de variantes → cache _flick_cache reste petit
        """
        for light in self.lights:
            if light["flicker"]:
                light["_phase"] += dt * light["flicker_speed"]
                # sin oscille entre -1 et +1 → raw oscille entre 165 et 255.
                raw = 210 + 45 * math.sin(light["_phase"])
                # Astuce binaire : >>3 divise par 8, <<3 multiplie par 8.
                # Faire les deux à la suite = arrondir à un multiple de 8.
                # Exemple : 213 → >>3 = 26 → <<3 = 208.
                light["_alpha"] = (int(raw) >> 3) << 3

    # ═════════════════════════════════════════════════════════════════════════
    #  4. CHARGEMENT DES TEXTURES (lazy : à la 1re utilisation seulement)
    # ═════════════════════════════════════════════════════════════════════════

    def _load_textures(self):
        """Charge les images de halos. "Lazy" = pas avant d'en avoir besoin.

        Pourquoi pas dans __init__ ? Parce que pygame.image.load() exige
        que pygame soit initialisé ET qu'une fenêtre soit créée. En faisant
        le chargement à la 1re utilisation, on évite les ennuis si on
        instancie LightingSystem trop tôt.
        """
        if hasattr(self, '_textures'):
            return    # déjà fait

        self._textures = {}
        # Mapping  type de lumière  →  fichier image
        names = {
            "player":     "light_player.png",     # halo du joueur
            "torch":      "light_medium.png",     # torche
            "large":      "light_large.png",      # grande zone
            "cool":       "light_cool.png",       # tendance bleue/froide
            "dim":        "light_dim.png",        # faible (pour ennemis)
            "background": "light_background.png", # ambiance arrière-plan
        }
        for k, fname in names.items():
            path = os.path.join(_IMG_DIR, fname)
            # convert() = adapte au format de la fenêtre → blit plus rapide.
            self._textures[k] = pygame.image.load(path).convert()

    # ═════════════════════════════════════════════════════════════════════════
    #  5. RÉCUPÉRATION D'UN HALO (avec cache)
    # ═════════════════════════════════════════════════════════════════════════

    def _get_halo(self, radius, ltype):
        """Renvoie le halo redimensionné pour (rayon, type). Cache inclus.

        smoothscale = redimensionnement avec lissage (anti-aliasing) →
        plus joli qu'un scale brut, mais plus coûteux. Le cache fait que
        ce coût n'est payé qu'UNE fois par couple (rayon, type).
        """
        self._load_textures()
        key = (radius, ltype)
        if key not in self._cache:
            # Texture de secours = "torch" si le type demandé n'existe pas.
            tex  = self._textures.get(ltype, self._textures["torch"])
            size = max(2, radius * 2)
            self._cache[key] = pygame.transform.smoothscale(tex, (size, size))
        return self._cache[key]

    def _get_flick_halo(self, radius, ltype, alpha):
        """Halo modulé par un alpha, mis en cache par (rayon, type, alpha).

        Pourquoi un cache séparé ?
            Parce qu'on doit appliquer la modulation alpha (BLEND_RGB_MULT)
            sur le halo de base. Sans cache, on referait cette opération
            60 fois par seconde par lumière → coûteux.
            Grâce à la quantification de l'alpha (cf. update), il y a au
            plus ~12 valeurs distinctes par couple (rayon, type) → le cache
            ne contient au pire que ~12 entrées par lumière scintillante.
        """
        key = (radius, ltype, alpha)
        if key not in self._flick_cache:
            base = self._get_halo(radius, ltype)
            surf = base.copy()
            # Multiplier le halo par (alpha, alpha, alpha) → réduit son intensité.
            # Plus alpha est petit, plus le halo est sombre.
            surf.fill((alpha, alpha, alpha), special_flags=pygame.BLEND_RGB_MULT)
            self._flick_cache[key] = surf

            # Sécurité : si jamais le cache explose (anomalie), on en vire
            # la moitié pour ne pas saturer la mémoire.
            if len(self._flick_cache) > 256:
                keys = list(self._flick_cache.keys())
                for k in keys[:128]:
                    del self._flick_cache[k]
        return self._flick_cache[key]

    # ═════════════════════════════════════════════════════════════════════════
    #  6. RENDU FINAL — applique l'éclairage sur l'écran
    # ═════════════════════════════════════════════════════════════════════════

    def render(self, surf, camera, player_rect):
        """Assombrit `surf` partout sauf autour du joueur et des lumières.

        Étapes (cf. en-tête du fichier pour le schéma général) :
            1) Recréer les surfaces tampons si l'écran a changé de taille.
            2) Remplir _darkness en noir.
            3) Ajouter (BLEND_ADD) le halo du joueur.
            4) Pour chaque lumière de la scène :
                 - skipper si hors écran (cull)
                 - récupérer le halo (avec ou sans flicker)
                 - l'ajouter (BLEND_ADD) → les halos se SOMMENT
            5) Fusionner avec _ambient (BLEND_MAX) → pas de noir absolu.
            6) Multiplier sur `surf` (BLEND_MULT) → assombrit le monde.
        """
        screen_w, screen_h = surf.get_size()

        # ── Étape 1 : (re)créer les tampons si la taille a changé ────────────
        # Pourquoi pas chaque frame ? Parce que créer une grosse Surface est
        # coûteux. On le fait UNE fois, et on réutilise l'objet.
        if (screen_w, screen_h) != self._screen_size:
            self._screen_size = (screen_w, screen_h)
            self._darkness = pygame.Surface((screen_w, screen_h))
            self._ambient  = pygame.Surface((screen_w, screen_h))
            # FOND_ALPHA : niveau gris constant (genre 60). Plus haut = plus
            # clair partout. Cette surface ne change pas → on la remplit
            # une seule fois et on la réutilise.
            self._ambient.fill((FOND_ALPHA, FOND_ALPHA, FOND_ALPHA))

        # ── Étape 2 : on repart d'un noir total chaque frame ────────────────
        self._darkness.fill((0, 0, 0))

        # ── Étape 3 : halo du joueur (toujours présent) ─────────────────────
        # Conversion world → écran via la caméra.
        sx   = player_rect.centerx - int(camera.offset_x)
        sy   = player_rect.centery - int(camera.offset_y)
        halo = self._get_halo(RAYON_JOUEUR, "player")
        # BLEND_RGB_ADD = additive blending → la lumière s'ajoute.
        # On positionne le halo CENTRÉ sur le joueur (d'où le -RAYON_JOUEUR).
        self._darkness.blit(halo, (sx - RAYON_JOUEUR, sy - RAYON_JOUEUR),
                            special_flags=pygame.BLEND_RGB_ADD)

        # ── Étape 4 : lumières de la scène ──────────────────────────────────
        for light in self.lights:
            lx = light["x"] - int(camera.offset_x)
            ly = light["y"] - int(camera.offset_y)
            r  = light["radius"]
            # CULL : si la lumière est hors écran, on saute.
            # Cas : lumière à droite (lx - r > screen_w), à gauche (lx + r < 0),
            #       au-dessus (ly + r < 0), en-dessous (ly - r > screen_h).
            if lx + r < 0 or lx - r > screen_w or ly + r < 0 or ly - r > screen_h:
                continue
            # Halo : version vibrante si flicker, version stable sinon.
            if light["flicker"]:
                halo = self._get_flick_halo(r, light["type"], light["_alpha"])
            else:
                halo = self._get_halo(r, light["type"])
            self._darkness.blit(halo, (lx - r, ly - r),
                                special_flags=pygame.BLEND_RGB_ADD)

        # ── Étape 5 : fusion avec l'ambiance ────────────────────────────────
        # BLEND_RGB_MAX = on garde la valeur MAX entre _darkness et _ambient,
        # canal par canal. Concrètement : les zones de _darkness plus sombres
        # que FOND_ALPHA (= les coins noirs) se voient relevées à FOND_ALPHA.
        # Les zones bien éclairées (déjà claires) restent claires.
        # → garantit qu'on n'a JAMAIS de noir absolu (= injouable).
        self._darkness.blit(self._ambient, (0, 0), special_flags=pygame.BLEND_RGB_MAX)

        # ── Étape 6 : application sur le monde ──────────────────────────────
        # BLEND_RGB_MULT = multiplie chaque pixel de surf par celui de _darkness
        # divisé par 255. Donc :
        #   pixel monde × 0   = 0      (noir → invisible)
        #   pixel monde × 255 = monde  (blanc → totalement visible)
        # C'est ce qui assombrit la scène hors des halos.
        surf.blit(self._darkness, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
