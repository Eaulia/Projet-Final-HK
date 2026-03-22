# ─────────────────────────────────────────
#  ENTRE-DEUX — Gestionnaire du mode histoire
# ─────────────────────────────────────────
#
#  Overlay accessible depuis l'éditeur (touche H).
#  Permet d'organiser les cartes par chapitres.
#  La première carte du premier chapitre = carte de départ de "Nouvelle partie".
#
#  Structure dans game_config.json :
#    "histoire": [
#       { "nom": "Chapitre 1", "maps": ["map1", "map2"] },
#       { "nom": "Chapitre 2", "maps": ["map3"] }
#    ]

import pygame
from systems.save_system import lire_config, ecrire_config


class GestionnaireHistoire:

    LARGEUR = 680
    LIGNE_H = 30

    def __init__(self):
        self.actif        = False
        self._chapitres   = []    # [{"nom": str, "maps": [str, ...]}, ...]
        self._maps_dispo  = []    # toutes les maps disponibles dans maps/
        self._boutons     = []    # [(rect, callback)] — reconstruits à chaque draw
        self._boutons_sub = []    # idem pour le sous-menu
        self._sous_menu   = None  # (ch_index, [options_maps]) — None si fermé
        self._saisie      = False # True = on saisit un nom de chapitre
        self._saisie_txt  = ""
        self._police      = None
        self._police_sm   = None
        self._scroll      = 0

    # ── Polices (lazy) ────────────────────────────────────────────────────

    def _init_polices(self):
        if self._police is None:
            self._police    = pygame.font.SysFont("Consolas", 16)
            self._police_sm = pygame.font.SysFont("Consolas", 13)

    # ── Ouverture / fermeture ─────────────────────────────────────────────

    def ouvrir(self, maps_dispo):
        config = lire_config()
        self._chapitres  = [
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
        self._sauvegarder()
        self.actif = False

    def _sauvegarder(self):
        config = lire_config()
        config["histoire"] = self._chapitres
        # Première carte du premier chapitre = carte de départ
        if self._chapitres and self._chapitres[0]["maps"]:
            config["carte_debut"] = self._chapitres[0]["maps"][0]
        else:
            config.pop("carte_debut", None)
        ecrire_config(config)

    # ── Gestion des événements ────────────────────────────────────────────

    def handle_event(self, event):
        """Retourne True si l'événement est consommé par le gestionnaire."""
        if not self.actif:
            return False

        self._init_polices()

        # Saisie d'un nom de chapitre
        if self._saisie:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    nom = self._saisie_txt.strip() or f"Chapitre {len(self._chapitres) + 1}"
                    self._chapitres.append({"nom": nom, "maps": []})
                    self._saisie     = False
                    self._saisie_txt = ""
                elif event.key == pygame.K_ESCAPE:
                    self._saisie     = False
                    self._saisie_txt = ""
                elif event.key == pygame.K_BACKSPACE:
                    self._saisie_txt = self._saisie_txt[:-1]
                else:
                    c = event.unicode
                    if c and c.isprintable():
                        self._saisie_txt += c
            return True

        # Échap ferme le sous-menu ou le gestionnaire
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self._sous_menu is not None:
                    self._sous_menu = None
                else:
                    self.fermer()
                return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self._sous_menu is not None:
                # Clic dans le sous-menu
                for rect, cb in self._boutons_sub:
                    if rect.collidepoint(pos):
                        cb(); return True
                self._sous_menu = None
                return True
            for rect, cb in self._boutons:
                if rect.collidepoint(pos):
                    cb(); return True

        if event.type == pygame.MOUSEWHEEL:
            self._scroll = max(0, self._scroll - event.y * self.LIGNE_H)

        return True   # consomme tout quand actif

    # ── Actions ───────────────────────────────────────────────────────────

    def _ouvrir_sous_menu(self, ch_idx, sx, sy):
        deja    = set(self._chapitres[ch_idx]["maps"])
        options = [m for m in self._maps_dispo if m not in deja]
        self._sous_menu = (ch_idx, options, sx, sy)

    def _ajouter_map(self, ch_idx, nom_map):
        self._chapitres[ch_idx]["maps"].append(nom_map)
        self._sous_menu = None

    def _suppr_map(self, ch_idx, map_idx):
        self._chapitres[ch_idx]["maps"].pop(map_idx)

    def _suppr_chapitre(self, ch_idx):
        self._chapitres.pop(ch_idx)

    def _nouveau_chapitre(self):
        self._saisie     = True
        self._saisie_txt = ""

    # ── Rendu ─────────────────────────────────────────────────────────────

    def draw(self, surf):
        if not self.actif:
            return
        self._init_polices()
        w, h  = surf.get_size()
        font  = self._police
        sm    = self._police_sm
        lh    = self.LIGNE_H
        pw    = self.LARGEUR
        px    = (w - pw) // 2

        # Voile de fond
        voile = pygame.Surface((w, h), pygame.SRCALPHA)
        voile.fill((0, 0, 0, 190))
        surf.blit(voile, (0, 0))

        # Hauteur du panneau : 3 lignes fixes + contenu chapitres
        nb_lignes = sum(2 + len(c["maps"]) for c in self._chapitres) + 4
        ph        = min(nb_lignes * lh + 20, h - 60)
        py_pan    = (h - ph) // 2

        fond = pygame.Surface((pw, ph), pygame.SRCALPHA)
        fond.fill((8, 6, 20, 235))
        surf.blit(fond, (px, py_pan))
        pygame.draw.rect(surf, (100, 80, 200), (px, py_pan, pw, ph), 1)
        pygame.draw.rect(surf, (45, 35, 85),   (px+2, py_pan+2, pw-4, ph-4), 1)

        self._boutons = []
        zone_h = ph - lh * 2 - 24   # hauteur scrollable

        # Titre
        titre = font.render("MODE HISTOIRE — Chapitres & cartes", True, (200, 175, 255))
        surf.blit(titre, (px + (pw - titre.get_width()) // 2, py_pan + 10))
        pygame.draw.line(surf, (70, 55, 140),
                         (px + 14, py_pan + lh + 4),
                         (px + pw - 14, py_pan + lh + 4), 1)

        # Zone de défilement
        clip_rect = pygame.Rect(px, py_pan + lh + 6, pw, zone_h)
        surf.set_clip(clip_rect)

        y  = py_pan + lh + 8 - self._scroll
        cx = px + 14

        for ci, chapitre in enumerate(self._chapitres):

            if y > py_pan + ph - lh * 2: break

            # En-tête chapitre
            ch_surf = font.render(f"▶  {chapitre['nom']}", True, (255, 210, 70))
            surf.blit(ch_surf, (cx, y + 4))

            xbtn = px + pw - 34
            xr = pygame.Rect(xbtn, y + 2, 22, 22)
            pygame.draw.rect(surf, (120, 40, 40), xr, 1)
            surf.blit(sm.render("×", True, (255, 80, 80)), (xr.x + 5, xr.y + 3))
            self._boutons.append((xr, lambda c=ci: self._suppr_chapitre(c)))
            y += lh

            # Maps du chapitre
            for mi, nom_map in enumerate(chapitre["maps"]):
                etoile  = " ★" if mi == 0 and ci == 0 else ""
                couleur = (180, 255, 180) if mi == 0 and ci == 0 else (170, 170, 215)
                surf.blit(sm.render(f"   → {nom_map}{etoile}", True, couleur), (cx + 10, y + 5))

                mr = pygame.Rect(xbtn, y + 2, 22, 20)
                pygame.draw.rect(surf, (90, 35, 35), mr, 1)
                surf.blit(sm.render("×", True, (200, 70, 70)), (mr.x + 5, mr.y + 2))
                self._boutons.append((mr, lambda c=ci, m=mi: self._suppr_map(c, m)))
                y += lh - 4

            # Bouton + ajouter carte
            ar = pygame.Rect(cx + 10, y + 2, 200, 22)
            pygame.draw.rect(surf, (30, 70, 30), ar, 1)
            surf.blit(sm.render("+ Ajouter une carte", True, (80, 200, 80)), (ar.x + 6, ar.y + 3))
            self._boutons.append((ar, lambda c=ci, sx=ar.x, sy=ar.bottom: self._ouvrir_sous_menu(c, sx, sy)))
            y += lh

            pygame.draw.line(surf, (35, 30, 60),
                             (px + 10, y + 2), (px + pw - 10, y + 2), 1)
            y += 8

        surf.set_clip(None)

        # Boutons bas
        yb = py_pan + ph - lh - 8

        nb = pygame.Rect(px + 14, yb, 210, 26)
        pygame.draw.rect(surf, (25, 55, 25), nb, 1)
        surf.blit(font.render("+ Nouveau chapitre", True, (70, 190, 70)), (nb.x + 8, nb.y + 4))
        self._boutons.append((nb, self._nouveau_chapitre))

        aide = sm.render("★ = carte de départ  |  [Échap]=fermer", True, (90, 90, 130))
        surf.blit(aide, (px + pw // 2 - aide.get_width() // 2 + 20, yb + 5))

        fb = pygame.Rect(px + pw - 110, yb, 96, 26)
        pygame.draw.rect(surf, (50, 35, 75), fb, 1)
        surf.blit(font.render("Fermer", True, (190, 160, 255)), (fb.x + 12, fb.y + 4))
        self._boutons.append((fb, self.fermer))

        # Sous-menu sélection de carte
        if self._sous_menu is not None:
            self._draw_sous_menu(surf, sm)

        # Saisie de nom
        if self._saisie:
            self._draw_saisie(surf, w, h, font)

    def _draw_sous_menu(self, surf, font):
        ch_idx, options, ox, oy = self._sous_menu
        self._boutons_sub = []

        sw  = 240
        sh  = max(40, min(len(options) * 26 + 24, 280))
        sx  = min(ox, surf.get_width() - sw - 10)
        sy  = min(oy, surf.get_height() - sh - 10)

        fond = pygame.Surface((sw, sh), pygame.SRCALPHA)
        fond.fill((10, 12, 28, 245))
        surf.blit(fond, (sx, sy))
        pygame.draw.rect(surf, (80, 200, 80), (sx, sy, sw, sh), 1)

        surf.blit(font.render("Choisir :", True, (160, 240, 160)), (sx + 8, sy + 4))

        if not options:
            surf.blit(font.render("(aucune carte disponible)", True, (120, 120, 120)),
                      (sx + 8, sy + 24))
            return

        mpos = pygame.mouse.get_pos()
        y    = sy + 24
        for nom_map in options:
            r = pygame.Rect(sx + 6, y, sw - 12, 22)
            if r.collidepoint(mpos):
                pygame.draw.rect(surf, (30, 80, 30), r)
            surf.blit(font.render(nom_map, True, (210, 255, 210)), (r.x + 6, r.y + 3))
            self._boutons_sub.append((r, lambda n=nom_map, c=ch_idx: self._ajouter_map(c, n)))
            y += 26

    def _draw_saisie(self, surf, w, h, font):
        bw, bh = 420, 92
        bx, by = (w - bw) // 2, (h - bh) // 2
        fond = pygame.Surface((bw, bh), pygame.SRCALPHA)
        fond.fill((10, 10, 24, 245))
        surf.blit(fond, (bx, by))
        pygame.draw.rect(surf, (70, 180, 70), (bx, by, bw, bh), 1)
        surf.blit(font.render("Nom du chapitre :", True, (160, 240, 160)), (bx + 12, by + 10))
        surf.blit(font.render(self._saisie_txt + "_", True, (255, 255, 255)), (bx + 12, by + 40))
        surf.blit(self._police_sm.render("[Entrée] valider  [Échap] annuler",
                                         True, (100, 100, 140)), (bx + 12, by + 68))
