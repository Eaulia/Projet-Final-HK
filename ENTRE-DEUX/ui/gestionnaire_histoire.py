# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Gestionnaire du mode histoire
# ─────────────────────────────────────────────────────────────────────────────
#
#  À QUOI SERT CE FICHIER ?
#  ------------------------
#  Un overlay (= petit menu superposé) qui s'ouvre depuis l'éditeur avec
#  la touche [H]. Il sert à organiser les cartes du jeu en chapitres :
#
#       Chapitre 1 ▶
#         → map1   ★   (la première carte du premier chapitre = carte de départ)
#         → map2
#         + Ajouter une carte
#       Chapitre 2 ▶
#         → map3
#       + Nouveau chapitre
#
#  Cet ordre détermine l'enchaînement quand on lance "Nouvelle partie".
#
#  STRUCTURE STOCKÉE dans game_config.json (clé "histoire") :
#      "histoire": [
#         { "nom": "Chapitre 1", "maps": ["map1", "map2"] },
#         { "nom": "Chapitre 2", "maps": ["map3"] }
#      ]
#  Et la clé "carte_debut" pointe sur la 1re carte du 1er chapitre.
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  world/editor.py instancie le gestionnaire :
#       self.gestionnaire_histoire = GestionnaireHistoire()
#  La touche [H] dans l'éditeur appelle :
#       self.gestionnaire_histoire.ouvrir(maps_dispo)
#  Et chaque frame, si actif :
#       self.gestionnaire_histoire.handle_event(event)   # consomme tout
#       self.gestionnaire_histoire.draw(screen)
#
#  JE VEUX MODIFIER QUOI ?
#  -----------------------
#     - Ajouter une action sur un chapitre  → méthode _… + bouton dans draw()
#     - Changer l'apparence (couleurs)      → littéraux RGB dans draw / _draw_*
#     - Largeur du panneau                  → constante LARGEUR
#     - Hauteur d'une ligne                 → constante LIGNE_H
#     - Format du fichier histoire          → ouvrir() / _sauvegarder()
#
#  ASTUCE LAMBDA :
#  ---------------
#  Pour câbler les boutons "supprimer" et "ajouter map", on stocke une liste
#  de tuples (rect, callback). Les callbacks sont des lambdas avec une
#  capture par défaut (lambda c=ci: ...). Le `c=ci` est essentiel — sans
#  lui, toutes les lambdas verraient la dernière valeur de la boucle, et
#  cliquer sur n'importe quel chapitre supprimerait toujours le dernier.
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D1]  pygame.Surface       — voile + fonds des panneaux
#     [D2]  SRCALPHA             — transparence des panneaux
#     [D4]  pygame.Rect          — zones cliquables des boutons
#     [D5]  colliderect          — détecter les clics (collidepoint en fait)
#     [D33] List comprehension   — _ouvrir_sous_menu (filtrer maps libres)
#     [D34] Lambda               — callbacks des boutons (avec c=ci !)
#     [D35] JSON                 — game_config.json via save_system
#
# ─────────────────────────────────────────────────────────────────────────────

import pygame
from systems.save_system import lire_config, ecrire_config


class GestionnaireHistoire:
    """Gère l'organisation des cartes en chapitres (overlay touche [H])."""

    # ═════════════════════════════════════════════════════════════════════════
    #  1. CONSTANTES DE MISE EN PAGE
    # ═════════════════════════════════════════════════════════════════════════

    LARGEUR = 680   # largeur du panneau principal (pixels)
    LIGNE_H = 30    # hauteur d'une ligne (titre, map, bouton)

    # ═════════════════════════════════════════════════════════════════════════
    #  2. CONSTRUCTION
    # ═════════════════════════════════════════════════════════════════════════

    def __init__(self):
        # État principal
        self.actif        = False

        # Données chargées depuis game_config.json à l'ouverture.
        # Format : [{"nom": str, "maps": [str, ...]}, ...]
        self._chapitres   = []
        self._maps_dispo  = []   # toutes les maps présentes dans maps/

        # Boutons cliquables : (Rect, callback_lambda).
        # Reconstruits ENTIÈREMENT à chaque draw() — c'est plus simple
        # que de tenir une structure persistante alors que les chapitres
        # bougent en permanence.
        self._boutons     = []
        self._boutons_sub = []

        # Sous-menu "+ Ajouter une carte" : None si fermé, sinon un tuple
        # (ch_index, options_maps, sx, sy) pour savoir quoi proposer et où.
        self._sous_menu   = None

        # Saisie clavier d'un nom de chapitre (popup centré)
        self._saisie      = False
        self._saisie_txt  = ""

        # Polices initialisées paresseusement
        self._police      = None
        self._police_sm   = None

        # Décalage vertical (molette de souris)
        self._scroll      = 0

    # ═════════════════════════════════════════════════════════════════════════
    #  3. POLICES (initialisation paresseuse)
    # ═════════════════════════════════════════════════════════════════════════

    def _init_polices(self):
        """Charge les polices au premier draw (pygame.font.init() doit être passé)."""
        if self._police is None:
            self._police    = pygame.font.SysFont("Consolas", 16)
            self._police_sm = pygame.font.SysFont("Consolas", 13)

    # ═════════════════════════════════════════════════════════════════════════
    #  4. OUVERTURE / FERMETURE / SAUVEGARDE
    # ═════════════════════════════════════════════════════════════════════════

    def ouvrir(self, maps_dispo):
        """Ouvre l'overlay. `maps_dispo` = liste des noms de cartes existantes."""
        config = lire_config()

        # On copie les chapitres pour pouvoir les modifier sans toucher
        # à la config originale (au cas où l'utilisateur ferme avec Échap
        # avant la sauvegarde — actuellement on sauve toujours, mais
        # cette copie défensive ne coûte rien).
        # List comprehension [D33] : transforme chaque chapitre du JSON
        # en un dict simple à deux clés.
        self._chapitres = [
            {"nom": c["nom"], "maps": list(c["maps"])}
            for c in config.get("histoire", [])
        ]
        self._maps_dispo = maps_dispo
        self.actif       = True
        self._sous_menu  = None
        self._saisie     = False
        self._saisie_txt = ""
        self._scroll     = 0

    def fermer(self):
        """Sauvegarde puis ferme l'overlay."""
        self._sauvegarder()
        self.actif = False

    def _sauvegarder(self):
        """Écrit les chapitres dans game_config.json [D35]."""
        config = lire_config()
        config["histoire"] = self._chapitres

        # La carte de départ = première carte du premier chapitre.
        # Si plus aucun chapitre / aucune map → on retire la clé pour
        # signaler qu'il n'y a pas de carte par défaut.
        if self._chapitres and self._chapitres[0]["maps"]:
            config["carte_debut"] = self._chapitres[0]["maps"][0]
        else:
            config.pop("carte_debut", None)
        ecrire_config(config)

    # ═════════════════════════════════════════════════════════════════════════
    #  5. GESTION DES ÉVÉNEMENTS (clavier + souris)
    # ═════════════════════════════════════════════════════════════════════════
    #
    #  Cette méthode renvoie True si l'événement a été consommé. Quand
    #  l'overlay est actif, ELLE CONSOMME TOUT — même un clic dans le
    #  vide. Cela évite que l'éditeur derrière reçoive les clics aussi.

    def handle_event(self, event):
        """Renvoie True si l'événement est consommé par le gestionnaire."""

        if not self.actif:
            return False
        self._init_polices()

        # ── Mode "saisie d'un nom de chapitre" : on capture toutes les touches
        if self._saisie:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Si l'utilisateur n'a rien tapé, on génère un nom par
                    # défaut "Chapitre N+1" pour ne pas créer un chapitre vide.
                    nom = self._saisie_txt.strip() or f"Chapitre {len(self._chapitres) + 1}"
                    self._chapitres.append({"nom": nom, "maps": []})
                    self._saisie     = False
                    self._saisie_txt = ""
                elif event.key == pygame.K_ESCAPE:
                    # Annulation : on jette la saisie en cours
                    self._saisie     = False
                    self._saisie_txt = ""
                elif event.key == pygame.K_BACKSPACE:
                    self._saisie_txt = self._saisie_txt[:-1]
                else:
                    # event.unicode = caractère texte (ex: "é"), à utiliser
                    # plutôt que pygame.key.name() pour gérer les accents.
                    c = event.unicode
                    if c and c.isprintable():
                        self._saisie_txt += c
            return True

        # ── Échap : ferme le sous-menu, ou ferme le gestionnaire ─────────────
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self._sous_menu is not None:
                    self._sous_menu = None
                else:
                    self.fermer()
                return True

        # ── Clic gauche : on teste tous les rects cliquables ─────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Un sous-menu est ouvert : on teste D'ABORD ses boutons,
            # sinon on le ferme (clic à côté = annuler).
            if self._sous_menu is not None:
                for rect, cb in self._boutons_sub:
                    if rect.collidepoint(pos):
                        cb()
                        return True
                self._sous_menu = None
                return True

            # Sinon, boutons du panneau principal
            for rect, cb in self._boutons:
                if rect.collidepoint(pos):
                    cb()
                    return True

        # ── Molette : faire défiler la liste des chapitres ───────────────────
        if event.type == pygame.MOUSEWHEEL:
            self._scroll = max(0, self._scroll - event.y * self.LIGNE_H)

        # On consomme tout quand l'overlay est actif (l'éditeur derrière
        # ne doit pas voir les clics qui ratent les boutons).
        return True

    # ═════════════════════════════════════════════════════════════════════════
    #  6. ACTIONS (appelées par les callbacks des boutons)
    # ═════════════════════════════════════════════════════════════════════════

    def _ouvrir_sous_menu(self, ch_idx, sx, sy):
        """Ouvre le petit menu "Choisir une carte" à côté du bouton +."""
        # On filtre : on ne propose que les maps PAS DÉJÀ dans ce chapitre
        # (sinon on pourrait l'ajouter deux fois).
        deja    = set(self._chapitres[ch_idx]["maps"])
        options = [m for m in self._maps_dispo if m not in deja]   # [D33]
        self._sous_menu = (ch_idx, options, sx, sy)

    def _ajouter_map(self, ch_idx, nom_map):
        """Ajoute une map à un chapitre (et ferme le sous-menu)."""
        self._chapitres[ch_idx]["maps"].append(nom_map)
        self._sous_menu = None

    def _suppr_map(self, ch_idx, map_idx):
        """Retire une map d'un chapitre (sans confirmation — c'est un éditeur)."""
        self._chapitres[ch_idx]["maps"].pop(map_idx)

    def _suppr_chapitre(self, ch_idx):
        """Retire un chapitre entier."""
        self._chapitres.pop(ch_idx)

    def _nouveau_chapitre(self):
        """Active le mode saisie pour créer un nouveau chapitre."""
        self._saisie     = True
        self._saisie_txt = ""

    # ═════════════════════════════════════════════════════════════════════════
    #  7. RENDU — panneau principal
    # ═════════════════════════════════════════════════════════════════════════

    def draw(self, surf):
        """Dessine tout l'overlay si actif."""

        if not self.actif:
            return
        self._init_polices()

        w, h  = surf.get_size()
        font  = self._police
        sm    = self._police_sm
        lh    = self.LIGNE_H
        pw    = self.LARGEUR
        px    = (w - pw) // 2

        # ── Voile assombrissant tout l'écran ─────────────────────────────────
        voile = pygame.Surface((w, h), pygame.SRCALPHA)
        voile.fill((0, 0, 0, 190))
        surf.blit(voile, (0, 0))

        # ── Hauteur du panneau : fonction du nombre total de lignes ──────────
        # 2 lignes par chapitre (titre + bouton "+ Ajouter") + une par map.
        # On ajoute 4 lignes pour les marges et le titre du panneau.
        nb_lignes = sum(2 + len(c["maps"]) for c in self._chapitres) + 4
        ph        = min(nb_lignes * lh + 20, h - 60)
        py_pan    = (h - ph) // 2

        # ── Fond du panneau ──────────────────────────────────────────────────
        fond = pygame.Surface((pw, ph), pygame.SRCALPHA)
        fond.fill((8, 6, 20, 235))
        surf.blit(fond, (px, py_pan))
        # Double bordure : violet vif extérieur + violet sombre intérieur
        pygame.draw.rect(surf, (100, 80, 200), (px, py_pan, pw, ph), 1)
        pygame.draw.rect(surf, (45, 35, 85),   (px + 2, py_pan + 2, pw - 4, ph - 4), 1)

        # On RÉINITIALISE la liste des boutons : tous ceux d'avant sont caducs
        # (positions différentes après scroll, suppression, ajout…).
        self._boutons = []
        zone_h = ph - lh * 2 - 24   # hauteur disponible pour la liste

        # ── Titre du panneau + ligne de séparation ───────────────────────────
        titre = font.render("MODE HISTOIRE — Chapitres & cartes", True, (200, 175, 255))
        surf.blit(titre, (px + (pw - titre.get_width()) // 2, py_pan + 10))
        pygame.draw.line(surf, (70, 55, 140),
                         (px + 14, py_pan + lh + 4),
                         (px + pw - 14, py_pan + lh + 4), 1)

        # ── Zone scrollable (clip = limite le rendu à un Rect) ───────────────
        # set_clip empêche les éléments de "déborder" du panneau quand on
        # scrolle. À ne pas oublier le set_clip(None) plus bas !
        clip_rect = pygame.Rect(px, py_pan + lh + 6, pw, zone_h)
        surf.set_clip(clip_rect)

        y  = py_pan + lh + 8 - self._scroll
        cx = px + 14

        # ── Pour chaque chapitre : titre, maps, bouton "+", séparateur ───────
        for ci, chapitre in enumerate(self._chapitres):

            # Optimisation : si on est déjà sous le panneau, inutile de
            # continuer (les rendus seraient clippés de toute façon).
            if y > py_pan + ph - lh * 2:
                break

            # En-tête chapitre (▶ Nom)
            ch_surf = font.render(f"▶  {chapitre['nom']}", True, (255, 210, 70))
            surf.blit(ch_surf, (cx, y + 4))

            # Bouton × pour supprimer le chapitre
            xbtn = px + pw - 34
            xr = pygame.Rect(xbtn, y + 2, 22, 22)
            pygame.draw.rect(surf, (120, 40, 40), xr, 1)
            surf.blit(sm.render("×", True, (255, 80, 80)), (xr.x + 5, xr.y + 3))
            # ATTENTION lambda c=ci : capture par défaut [D34] — sans ça,
            # toutes les lambdas pointeraient sur le dernier chapitre.
            self._boutons.append((xr, lambda c=ci: self._suppr_chapitre(c)))
            y += lh

            # Maps du chapitre (la première du chapitre 0 a une étoile ★)
            for mi, nom_map in enumerate(chapitre["maps"]):
                if mi == 0 and ci == 0:
                    etoile  = " ★"
                    couleur = (180, 255, 180)   # vert pâle = carte de départ
                else:
                    etoile  = ""
                    couleur = (170, 170, 215)
                surf.blit(sm.render(f"   → {nom_map}{etoile}", True, couleur), (cx + 10, y + 5))

                # Bouton × pour retirer cette map du chapitre
                mr = pygame.Rect(xbtn, y + 2, 22, 20)
                pygame.draw.rect(surf, (90, 35, 35), mr, 1)
                surf.blit(sm.render("×", True, (200, 70, 70)), (mr.x + 5, mr.y + 2))
                # Capture par défaut [D34] de c et m (ci et mi)
                self._boutons.append((mr, lambda c=ci, m=mi: self._suppr_map(c, m)))
                y += lh - 4

            # Bouton "+ Ajouter une carte"
            ar = pygame.Rect(cx + 10, y + 2, 200, 22)
            pygame.draw.rect(surf, (30, 70, 30), ar, 1)
            surf.blit(sm.render("+ Ajouter une carte", True, (80, 200, 80)), (ar.x + 6, ar.y + 3))
            # Capture par défaut + position du sous-menu (sx, sy)
            self._boutons.append(
                (ar, lambda c=ci, sx=ar.x, sy=ar.bottom: self._ouvrir_sous_menu(c, sx, sy))
            )
            y += lh

            # Petit séparateur entre chapitres
            pygame.draw.line(surf, (35, 30, 60),
                             (px + 10, y + 2), (px + pw - 10, y + 2), 1)
            y += 8

        # ⚠️ TRÈS IMPORTANT : on retire le clip, sinon le reste du jeu
        # serait dessiné uniquement dans cette zone restreinte.
        surf.set_clip(None)

        # ── Boutons en bas du panneau (fixes, hors zone scrollable) ──────────
        yb = py_pan + ph - lh - 8

        # "+ Nouveau chapitre"
        nb = pygame.Rect(px + 14, yb, 210, 26)
        pygame.draw.rect(surf, (25, 55, 25), nb, 1)
        surf.blit(font.render("+ Nouveau chapitre", True, (70, 190, 70)), (nb.x + 8, nb.y + 4))
        self._boutons.append((nb, self._nouveau_chapitre))

        # Petit hint au centre
        aide = sm.render("★ = carte de départ  |  [Échap]=fermer", True, (90, 90, 130))
        surf.blit(aide, (px + pw // 2 - aide.get_width() // 2 + 20, yb + 5))

        # "Fermer"
        fb = pygame.Rect(px + pw - 110, yb, 96, 26)
        pygame.draw.rect(surf, (50, 35, 75), fb, 1)
        surf.blit(font.render("Fermer", True, (190, 160, 255)), (fb.x + 12, fb.y + 4))
        self._boutons.append((fb, self.fermer))

        # ── Couches au-dessus : sous-menu et popup de saisie ─────────────────
        if self._sous_menu is not None:
            self._draw_sous_menu(surf, sm)

        if self._saisie:
            self._draw_saisie(surf, w, h, font)

    # ═════════════════════════════════════════════════════════════════════════
    #  8. RENDU — sous-menu "Choisir une carte"
    # ═════════════════════════════════════════════════════════════════════════

    def _draw_sous_menu(self, surf, font):
        """Petite popup verte avec la liste des maps disponibles."""

        ch_idx, options, ox, oy = self._sous_menu
        # On reconstruit aussi la liste de boutons du sous-menu à chaque draw.
        self._boutons_sub = []

        sw  = 240
        sh  = max(40, min(len(options) * 26 + 24, 280))
        # On clamp pour que la popup ne déborde pas de l'écran.
        sx  = min(ox, surf.get_width() - sw - 10)
        sy  = min(oy, surf.get_height() - sh - 10)

        # Fond de la popup (semi-transparent + bordure verte)
        fond = pygame.Surface((sw, sh), pygame.SRCALPHA)
        fond.fill((10, 12, 28, 245))
        surf.blit(fond, (sx, sy))
        pygame.draw.rect(surf, (80, 200, 80), (sx, sy, sw, sh), 1)

        surf.blit(font.render("Choisir :", True, (160, 240, 160)), (sx + 8, sy + 4))

        # Cas particulier : aucune map disponible (tout est déjà placé).
        if not options:
            surf.blit(font.render("(aucune carte disponible)", True, (120, 120, 120)),
                      (sx + 8, sy + 24))
            return

        # Liste des maps avec effet survol (highlight vert)
        mpos = pygame.mouse.get_pos()
        y    = sy + 24
        for nom_map in options:
            r = pygame.Rect(sx + 6, y, sw - 12, 22)
            if r.collidepoint(mpos):
                pygame.draw.rect(surf, (30, 80, 30), r)
            surf.blit(font.render(nom_map, True, (210, 255, 210)), (r.x + 6, r.y + 3))
            # Capture par défaut [D34] de n (nom_map) et c (ch_idx)
            self._boutons_sub.append(
                (r, lambda n=nom_map, c=ch_idx: self._ajouter_map(c, n))
            )
            y += 26

    # ═════════════════════════════════════════════════════════════════════════
    #  9. RENDU — popup "Saisir nom du chapitre"
    # ═════════════════════════════════════════════════════════════════════════

    def _draw_saisie(self, surf, w, h, font):
        """Petit cadre central avec un champ de texte (curseur "_" qui clignote… non, fixe)."""

        bw, bh = 420, 92
        bx, by = (w - bw) // 2, (h - bh) // 2

        # Fond + bordure verte
        fond = pygame.Surface((bw, bh), pygame.SRCALPHA)
        fond.fill((10, 10, 24, 245))
        surf.blit(fond, (bx, by))
        pygame.draw.rect(surf, (70, 180, 70), (bx, by, bw, bh), 1)

        # Titre du popup
        surf.blit(font.render("Nom du chapitre :", True, (160, 240, 160)),
                  (bx + 12, by + 10))
        # Texte tapé + un "_" pour faire un curseur (statique).
        surf.blit(font.render(self._saisie_txt + "_", True, (255, 255, 255)),
                  (bx + 12, by + 40))
        # Hint
        surf.blit(self._police_sm.render("[Entrée] valider  [Échap] annuler",
                                         True, (100, 100, 140)),
                  (bx + 12, by + 68))
