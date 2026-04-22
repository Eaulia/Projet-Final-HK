# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Panneau d'aide (touche F1)
# ─────────────────────────────────────────────────────────────────────────────
#
#  À QUOI SERT CE FICHIER ?
#  ------------------------
#  Tu joues, tu as oublié quelle touche fait quoi → tu appuies sur F1.
#  Un panneau apparaît au milieu de l'écran avec la liste des contrôles
#  organisée en 4 sections (Déplacement / Combat / Éditeur / Système).
#  F1 ou Échap pour le refermer.
#
#  Le panneau est un OVERLAY : il se dessine PAR-DESSUS le jeu (qui
#  continue ou est en pause derrière, selon le contexte). Le jeu n'est
#  pas modifié, on superpose juste un rectangle semi-transparent.
#
#  EXEMPLE CONCRET (ce que tu vois)
#  --------------------------------
#       ┌────────────────────────────────────┐
#       │             CONTRÔLES              │
#       │                                    │
#       │   Déplacement                      │
#       │     Q / D       Gauche / Droite    │
#       │     Espace      Sauter (...)       │
#       │     Shift       Dash (cooldown...) │
#       │     ...                            │
#       │                                    │
#       │   Combat & Interactions            │
#       │     F           Attaquer           │
#       │     ...                            │
#       │                                    │
#       │       F1 ou Échap pour fermer      │
#       └────────────────────────────────────┘
#
#  COMMENT C'EST CONSTRUIT ?
#  -------------------------
#  La liste des touches est STATIQUE, dans la variable _SECTIONS, juste
#  en dessous. C'est volontairement simple : pour ajouter / modifier une
#  ligne, on touche UNE liste, rien d'autre. Pas de fichier de config,
#  pas de système d'i18n compliqué. Si un jour tu veux traduire, c'est
#  ici qu'il faudra brancher gettext (ou autre).
#
#  Petit lexique :
#     - overlay    = "couche superposée". Une image rendue PAR-DESSUS
#                    l'image principale. Le jeu en dessous n'est pas
#                    modifié, on l'enrichit visuellement.
#     - SRCALPHA   = drapeau pygame "cette surface a un canal de
#                    transparence par pixel". Indispensable pour que le
#                    fond du panneau soit semi-transparent (on voit le
#                    jeu derrière, en plus sombre).
#     - blit       = "coller une image sur une autre". screen.blit(img, (x, y))
#                    veut dire "dessine img à la position (x, y) sur l'écran".
#     - SysFont    = police système. SysFont("Consolas", 28) prend la police
#                    "Consolas" (à largeur fixe, jolie pour des touches)
#                    en taille 28. Si la police n'est pas installée, pygame
#                    se rabat sur une police par défaut (rien ne plante).
#     - tuple RGBA = (rouge, vert, bleu, alpha). Chaque valeur entre 0 et 255.
#                    Ex : (15, 18, 30, 230) = bleu très sombre, presque opaque.
#     - lazy init  = "initialisation paresseuse" : on ne crée les polices
#                    qu'à la PREMIÈRE ouverture du panneau, pas au démarrage
#                    du jeu. Du coup, si tu n'ouvres jamais l'aide,
#                    pygame.font n'est jamais sollicité. Économie discrète,
#                    mais ça évite aussi un crash si pygame.font.init()
#                    n'a pas encore été appelé au moment où on construit
#                    l'overlay.
#
#  POURQUOI _font_xxx = None DANS __init__, ET INIT À LA 1RE FRAME ?
#  -----------------------------------------------------------------
#  Cf. "lazy init" du lexique. On crée le HelpOverlay très tôt (au
#  démarrage du jeu), parfois AVANT que pygame.font soit prêt. En
#  reportant la création des polices au premier draw(), on est sûrs
#  que pygame est complètement initialisé.
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  core/game.py instancie self.help_overlay = HelpOverlay() au démarrage,
#  appelle self.help_overlay.toggle() quand on appuie sur F1, et
#  self.help_overlay.draw(screen) à chaque frame (le draw retourne tout
#  de suite si visible == False, donc coût quasi-nul si fermé).
#
#  JE VEUX MODIFIER QUOI ?
#  -----------------------
#     - Ajouter / modifier des touches      → liste _SECTIONS ci-dessous
#     - Couleurs                            → constantes COULEUR_xxx
#     - Police, taille                      → méthode _init_fonts()
#     - Position / taille du panneau        → début de draw() (panel_w, etc.)
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D14]  pygame.Surface  — image hors-écran qu'on construit puis qu'on blit
#     [D17]  alpha           — transparence (4ᵉ valeur du tuple couleur)
#     [D19]  overlay         — couche superposée à l'image principale
#
# ─────────────────────────────────────────────────────────────────────────────

import pygame


# ═════════════════════════════════════════════════════════════════════════════
#  1. CONTENU DU PANNEAU (modifie ICI pour changer les touches affichées)
# ═════════════════════════════════════════════════════════════════════════════
#
#  Format : liste de sections.
#       Une section = (titre, liste de couples (touche, description))
#
#  Pour AJOUTER une nouvelle ligne dans une section : ajoute un tuple
#  (touche, description) dans la liste de touches de la section concernée.
#
#  Pour AJOUTER UNE SECTION : ajoute un nouveau tuple (titre, [...]) dans
#  _SECTIONS. Elle apparaîtra automatiquement, dans l'ordre où elle est
#  écrite ici.

_SECTIONS = [
    ("Déplacement", [
        ("Q / D",            "Gauche / Droite"),
        ("Espace",           "Sauter (double-saut en l'air)"),
        ("Shift",            "Dash (cooldown 0.5 s)"),
        ("S + F en l'air",   "Attaque vers le bas (pogo sur ennemi)"),
        ("Contre un mur",    "Wall-slide → Espace = wall-jump"),
        ("Z / ↑",            "Regarder en haut (affiche la vie)"),
    ]),
    ("Combat & Interactions", [
        ("F",                "Attaquer"),
        ("E",                "Parler à un PNJ / Ouvrir l'éditeur"),
        ("C",                "Rappeler / faire sortir les compagnons (cape)"),
        ("Tab",              "Inventaire"),
        ("Échap",            "Pause"),
    ]),
    ("Éditeur (mode éditeur)", [
        ("H",                "Gestionnaire d'histoire (cartes)"),
        ("Molette + Ctrl",   "Zoom / changement d'outil"),
        ("Clic molette",     "Caméra libre (pan)"),
    ]),
    ("Système", [
        ("F1",               "Ouvrir / fermer cette aide"),
    ]),
]


# ═════════════════════════════════════════════════════════════════════════════
#  2. COULEURS & STYLE
# ═════════════════════════════════════════════════════════════════════════════
#
#  Tuples RGBA (rouge, vert, bleu, alpha). Pour le fond, alpha=230 → on
#  voit ENCORE un peu le jeu derrière, mais largement assombri.
#  Pour les couleurs sans alpha (texte), pygame interprète RGB tout court.

COULEUR_FOND   = (15,  18,  30, 230)   # bleu nuit, semi-transparent
COULEUR_BORD   = (180, 180, 200)       # gris clair
COULEUR_TITRE  = (255, 235, 180)       # jaune doux (CONTRÔLES + sections)
COULEUR_TOUCHE = (180, 220, 255)       # bleu pâle (ex : "Espace")
COULEUR_DESC   = (220, 220, 220)       # blanc cassé (descriptions)


# ═════════════════════════════════════════════════════════════════════════════
#  3. LA CLASSE
# ═════════════════════════════════════════════════════════════════════════════

class HelpOverlay:
    def __init__(self):
        self.visible = False

        # Polices : on les crée plus tard (lazy init, cf. header).
        # Avoir des `None` ici sert juste à dire "champs déclarés, pas remplis".
        self._font_titre   = None
        self._font_section = None
        self._font_touche  = None
        self._font_desc    = None

    # ── Contrôles externes (appelés par game.py) ────────────────────────────

    def toggle(self):
        """F1 : on inverse l'état (ouvert → fermé, fermé → ouvert)."""
        self.visible = not self.visible

    def close(self):
        """Échap (ou tout ce qui veut forcer la fermeture)."""
        self.visible = False

    # ─────────────────────────────────────────────────────────────────────────
    #  RENDU (appelé chaque frame ; sort tout de suite si caché)
    # ─────────────────────────────────────────────────────────────────────────

    def draw(self, screen):
        # Caché → rien à faire (et c'est appelé 60 fois par seconde, donc
        # ce return tôt est important : il garde le coût à zéro quand on
        # n'a pas ouvert l'aide).
        if not self.visible:
            return

        self._init_fonts()                   # crée les polices au 1er appel
        w, h = screen.get_size()

        # ── Géométrie du panneau ────────────────────────────────────────────
        # Largeur cible : 640 px, mais jamais plus que la fenêtre - 60.
        # Idem pour la hauteur. min() garantit que le panneau RESTE dans
        # l'écran même si la fenêtre est petite.
        panel_w = min(640, w - 60)
        panel_h = min(540, h - 60)
        panel_x = (w - panel_w) // 2          # centré horizontalement
        panel_y = (h - panel_h) // 2          # centré verticalement

        # ── Fond + bordure ──────────────────────────────────────────────────
        # On crée une SURFACE INTERMÉDIAIRE de la taille du panneau, parce
        # qu'on veut un fond SEMI-TRANSPARENT (alpha=230 dans COULEUR_FOND).
        # Sans SRCALPHA, pygame ignorerait l'alpha → fond complètement opaque.
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill(COULEUR_FOND)
        pygame.draw.rect(panel, COULEUR_BORD, (0, 0, panel_w, panel_h), 2)
        screen.blit(panel, (panel_x, panel_y))

        # ── Titre "CONTRÔLES" centré en haut ────────────────────────────────
        titre = self._font_titre.render("CONTRÔLES", True, COULEUR_TITRE)
        screen.blit(titre, (panel_x + (panel_w - titre.get_width()) // 2,
                            panel_y + 18))

        # ── Sections ────────────────────────────────────────────────────────
        # On parcourt _SECTIONS et on dessine chaque ligne. La variable `y`
        # sert de "curseur d'écriture" : on l'incrémente après chaque ligne
        # pour ne pas écrire toutes les lignes les unes sur les autres.
        y = panel_y + 70
        for nom_section, touches in _SECTIONS:
            # Titre de la section (ex : "Déplacement")
            sec = self._font_section.render(nom_section, True, COULEUR_TITRE)
            screen.blit(sec, (panel_x + 28, y))
            y += sec.get_height() + 6

            # Lignes "touche  ───  description" alignées en deux colonnes
            for touche, desc in touches:
                t = self._font_touche.render(touche, True, COULEUR_TOUCHE)
                d = self._font_desc.render(desc, True, COULEUR_DESC)
                screen.blit(t, (panel_x + 48,  y))   # colonne 1 : touche
                screen.blit(d, (panel_x + 220, y))   # colonne 2 : description
                y += t.get_height() + 4

            y += 8                              # petite respiration entre sections

        # ── Hint de fermeture, en bas, centré ───────────────────────────────
        hint = self._font_desc.render("F1 ou Échap pour fermer", True, (150, 150, 160))
        screen.blit(hint, (panel_x + (panel_w - hint.get_width()) // 2,
                           panel_y + panel_h - 30))

    # ─────────────────────────────────────────────────────────────────────────
    #  INITIALISATION PARESSEUSE DES POLICES
    # ─────────────────────────────────────────────────────────────────────────

    def _init_fonts(self):
        """Crée les 4 polices au PREMIER appel à draw(). Les appels suivants
        ne font rien (court-circuit avec le `is None`).

        Pourquoi pas dans __init__ ? Parce qu'au moment où __init__ est
        appelé, pygame.font n'est peut-être pas encore prêt (ordre
        d'initialisation du jeu). En reportant à draw(), on est SÛRS
        que pygame est complètement initialisé.
        """
        if self._font_titre is None:
            self._font_titre   = pygame.font.SysFont("Consolas", 28, bold=True)
            self._font_section = pygame.font.SysFont("Consolas", 18, bold=True)
            self._font_touche  = pygame.font.SysFont("Consolas", 15, bold=True)
            self._font_desc    = pygame.font.SysFont("Consolas", 15)
