# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Boîte de dialogue style Undertale
# ─────────────────────────────────────────────────────────────────────────────
#
#  À QUOI SERT CE FICHIER ?
#  ------------------------
#  Une boîte de dialogue qui apparaît en bas de l'écran quand le joueur
#  parle à un PNJ. Elle :
#
#     - affiche le texte LETTRE PAR LETTRE (style Undertale / Pokémon)
#     - joue un petit "bip" à chaque caractère
#     - affiche le nom de l'orateur en doré
#     - affiche un ▼ clignotant quand la ligne est terminée
#     - passe à la ligne suivante quand le joueur appuie sur Espace/Entrée
#     - permet de sauter l'animation : appuyer pendant l'apparition affiche
#       tout le texte d'un coup
#
#  Le bip est GÉNÉRÉ EN MÉMOIRE (pas de fichier audio à charger), via une
#  petite synthèse sinusoïdale avec une enveloppe douce pour éviter le
#  "clic" au début et à la fin.
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  core/game.py crée l'instance :
#       self.dialogue_box = BoiteDialogue()
#  entities/npc.py l'appelle quand le joueur parle :
#       self.game.dialogue_box.demarrer(self.dialogue)
#  La boucle de jeu fait :
#       self.dialogue_box.update(dt)
#       self.dialogue_box.draw(screen)
#  Et game.py route la touche Espace vers self.dialogue_box.avancer().
#
#  JE VEUX MODIFIER QUOI ?
#  -----------------------
#     - Vitesse d'apparition du texte → constante VITESSE_LETTRE
#     - Hauteur de la boîte           → constante HAUTEUR_BOITE
#     - Couleurs                      → constantes COULEUR_*
#     - Son (fréquence, durée)        → _init_son()
#     - Largeur de retour à la ligne  → _decouper_texte()
#     - Nombre max de lignes affichées→ draw() ([:4] dans la boucle)
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D1]  pygame.Surface       — fond semi-transparent de la boîte
#     [D2]  SRCALPHA             — transparence du fond
#     [D3]  blit                 — collage du texte
#     [D10] dt                   — vitesse d'apparition lettre par lettre
#     [D12] math.sin             — synthèse audio + clignotement du ▼
#     [D22] Machine à états      — actif / tout_affiche
#
# ─────────────────────────────────────────────────────────────────────────────

import math
import struct
import pygame


class BoiteDialogue:
    """Boîte de dialogue façon Undertale (texte lettre par lettre + bip).

    Utilisation :
        boite.demarrer([("Bonjour !", "Nimbus"), ("...", "Nimbus")])
        boite.update(dt)       ← chaque frame
        boite.draw(surf)       ← chaque frame
        boite.avancer()        ← quand le joueur appuie sur Espace/Entrée
    """

    # ═════════════════════════════════════════════════════════════════════════
    #  1. CONSTANTES (style et timing)
    # ═════════════════════════════════════════════════════════════════════════

    VITESSE_LETTRE  = 0.034            # secondes entre deux lettres
    COULEUR_FOND    = (12, 12, 24, 218)  # bleu nuit semi-opaque (RGBA)
    COULEUR_BORD    = (170, 150, 255)  # bordure violette
    COULEUR_TEXTE   = (235, 235, 235)  # blanc cassé
    COULEUR_ORATEUR = (255, 215, 80)   # doré (comme dans Hollow Knight)
    HAUTEUR_BOITE   = 155              # pixels

    # ═════════════════════════════════════════════════════════════════════════
    #  2. CONSTRUCTION
    # ═════════════════════════════════════════════════════════════════════════

    def __init__(self):
        # État principal
        self.actif  = False

        # Données du dialogue en cours
        self._lignes         = []   # [(texte, orateur), ...]
        self._index          = 0    # index de la ligne en cours
        self._nb_car         = 0    # nombre de caractères révélés sur la ligne
        self._timer_lettre   = 0.0  # accumulateur (≥ VITESSE_LETTRE → +1 lettre)
        self._tout_affiche   = False

        # Animation du petit ▼ clignotant en bas à droite
        self._phase_cligno   = 0.0

        # Son de "bip" — généré à la première utilisation (lazy)
        self._son_bip        = None

        # Polices initialisées paresseusement
        self._police_orateur = None
        self._police_texte   = None

    # ═════════════════════════════════════════════════════════════════════════
    #  3. INITIALISATIONS PARESSEUSES (lazy : polices et son)
    # ═════════════════════════════════════════════════════════════════════════

    def _init_polices(self):
        """Charge les polices au premier draw."""
        if self._police_orateur is None:
            self._police_orateur = pygame.font.SysFont("Consolas", 17, bold=True)
            self._police_texte   = pygame.font.SysFont("Consolas", 16)

    def _init_son(self):
        """Génère un bip court directement en mémoire — pas de fichier audio.

        Fréquence et durée choisies pour imiter le son de dialogue
        d'Undertale. On synthétise une onde sinus [D12] avec une enveloppe
        douce (fade-in / fade-out) pour éviter le clic numérique au début
        et à la fin du son."""

        if self._son_bip is not None:
            return

        try:
            # Fréquence d'échantillonnage du mixer pygame (44100 Hz par défaut).
            freq_mix  = pygame.mixer.get_init()[0]
            frequence = 860      # Hz — voix légèrement métallique
            duree     = 0.038    # secondes
            volume    = 0.20     # 0.0 = silence, 1.0 = saturé

            nb_samples = int(freq_mix * duree)
            donnees    = bytearray()

            for i in range(nb_samples):
                # Enveloppe douce : 1.0 au milieu, → 0 aux extrémités sur ~7 ms.
                # Évite le "pop" qu'on entendrait sinon (transition brutale).
                env = min(1.0, min(i, nb_samples - i) / max(1, int(freq_mix * 0.007)))
                # Onde sinus * volume * enveloppe → entier 16 bits signé.
                val = int(volume * 32767 * env *
                          math.sin(2 * math.pi * frequence * i / freq_mix))
                # Clamp dans la plage int16 (sécurité).
                val = max(-32768, min(32767, val))
                # '<h' = little-endian, signed short (= int16) — format brut PCM.
                echantillon = struct.pack('<h', val)
                # Stéréo : on duplique le sample pour les canaux gauche et droit.
                donnees += echantillon + echantillon

            self._son_bip = pygame.mixer.Sound(buffer=bytes(donnees))

        except Exception:
            # Si le mixer n'est pas dispo (pas de carte son, mode CI…),
            # le jeu doit continuer à tourner — silencieusement.
            pass

    # ═════════════════════════════════════════════════════════════════════════
    #  4. API PUBLIQUE (demarrer, avancer)
    # ═════════════════════════════════════════════════════════════════════════

    def demarrer(self, lignes):
        """Démarre un dialogue.

        lignes : liste de tuples (texte, orateur)  ou  liste de strings simples.

        Exemple :
            boite.demarrer([
                ("Tu es tombé de bien haut.", "Nimbus"),
                ("...",                       "Nimbus"),
            ])
            boite.demarrer(["Première ligne", "Deuxième ligne"])  # sans orateur
        """

        # On normalise vers la forme tuple (texte, orateur). Si l'appelant
        # a passé des strings simples, on met un orateur vide.
        self._lignes = []
        for ligne in lignes:
            if isinstance(ligne, str):
                self._lignes.append((ligne, ""))
            else:
                self._lignes.append(tuple(ligne))

        # Reset complet de l'état d'animation
        self._index        = 0
        self._nb_car       = 0
        self._timer_lettre = 0.0
        self._tout_affiche = False
        self._phase_cligno = 0.0
        self.actif         = True

    def avancer(self):
        """Appelé quand le joueur appuie sur Espace ou Entrée.

        - Si la ligne n'est pas encore finie → affiche tout d'un coup.
        - Si la ligne est finie              → passe à la suivante (ou ferme)."""

        if not self.actif:
            return

        if not self._tout_affiche:
            # ── Étape "skip" : on révèle la ligne entière instantanément ─────
            self._nb_car       = len(self._lignes[self._index][0])
            self._tout_affiche = True
        else:
            # ── Étape "ligne suivante" ───────────────────────────────────────
            self._index += 1
            if self._index >= len(self._lignes):
                # Plus de ligne → on ferme la boîte
                self.actif = False
            else:
                # Reset de l'animation pour la nouvelle ligne
                self._nb_car       = 0
                self._timer_lettre = 0.0
                self._tout_affiche = False

    # ═════════════════════════════════════════════════════════════════════════
    #  5. UPDATE (animation lettre par lettre + son)
    # ═════════════════════════════════════════════════════════════════════════

    def update(self, dt):
        """Avance l'animation. dt = temps écoulé depuis la frame précédente [D10]."""

        if not self.actif:
            return

        # Animation continue du ▼ : 4 rad/s → un cycle complet ≈ 1.5 s.
        self._phase_cligno += dt * 4.0

        # Si tout est déjà affiché, plus rien à faire (à part le ▼ ci-dessus).
        if self._tout_affiche:
            return

        # ── Avance lettre par lettre ─────────────────────────────────────────
        self._init_son()
        texte = self._lignes[self._index][0]
        self._timer_lettre += dt

        # Boucle while plutôt que if : si dt est gros (frame qui a sauté),
        # on peut révéler PLUSIEURS lettres en une frame, sans rester en retard.
        while self._timer_lettre >= self.VITESSE_LETTRE and self._nb_car < len(texte):
            self._timer_lettre -= self.VITESSE_LETTRE
            self._nb_car += 1

            # Bip uniquement sur les caractères visibles (pas les espaces /
            # sauts de ligne) — sinon on entend "tac-tac…" pendant les blancs.
            dernier_char = texte[self._nb_car - 1]
            if dernier_char not in (' ', '\n') and self._son_bip:
                self._son_bip.play()

        # Quand on a tout révélé → on passe en mode "tout affiché" (▼ apparaît).
        if self._nb_car >= len(texte):
            self._tout_affiche = True

    # ═════════════════════════════════════════════════════════════════════════
    #  6. RENDU (boîte, orateur, texte, indicateur ▼)
    # ═════════════════════════════════════════════════════════════════════════

    def draw(self, surf):
        """Dessine la boîte si elle est active."""

        if not self.actif:
            return
        self._init_polices()

        # ── Position et taille de la boîte (ancrée en bas, marges fixes) ─────
        w, h    = surf.get_size()
        marge   = 28
        bx      = marge
        by      = h - self.HAUTEUR_BOITE - marge
        bw      = w - marge * 2
        bh      = self.HAUTEUR_BOITE

        # ── Fond semi-transparent ────────────────────────────────────────────
        # On passe par une Surface SRCALPHA [D1][D2] pour le canal alpha.
        fond = pygame.Surface((bw, bh), pygame.SRCALPHA)
        fond.fill(self.COULEUR_FOND)
        surf.blit(fond, (bx, by))

        # Double bordure (extérieure violet vif + intérieure plus sombre).
        pygame.draw.rect(surf, self.COULEUR_BORD, (bx, by, bw, bh), 2)
        pygame.draw.rect(surf, (60, 50, 110),
                         (bx + 4, by + 4, bw - 8, bh - 8), 1)

        texte, orateur = self._lignes[self._index]

        # ── Nom de l'orateur (en doré, en haut à gauche) ─────────────────────
        y_texte = by + 16
        if orateur:
            nom_surf = self._police_orateur.render(orateur, True, self.COULEUR_ORATEUR)
            surf.blit(nom_surf, (bx + 14, y_texte))
            y_texte += 28
            # Petite ligne sous le nom pour le détacher du texte
            pygame.draw.line(surf, (80, 65, 140),
                             (bx + 14, y_texte - 4),
                             (bx + 14 + nom_surf.get_width() + 20, y_texte - 4), 1)

        # ── Texte révélé jusqu'à _nb_car, avec retour à la ligne auto ────────
        texte_visible = texte[:self._nb_car]
        largeur_max   = bw - 30
        lignes_rendues = self._decouper_texte(texte_visible, largeur_max)

        # On limite à 4 lignes visibles ([:4]) — pour de plus longs textes,
        # mieux vaut découper en plusieurs entrées de la liste lignes.
        for i, ligne in enumerate(lignes_rendues[:4]):
            txt_surf = self._police_texte.render(ligne, True, self.COULEUR_TEXTE)
            surf.blit(txt_surf, (bx + 14, y_texte + i * 24))

        # ── Indicateur ▼ clignotant en bas à droite ──────────────────────────
        # alpha oscille entre 145 et 255 grâce à un sinus [D12].
        if self._tout_affiche:
            alpha    = int(200 + 55 * math.sin(self._phase_cligno))
            tri_surf = self._police_texte.render("▼", True, (alpha, alpha, alpha))
            surf.blit(tri_surf, (bx + bw - 26, by + bh - 26))

    # ═════════════════════════════════════════════════════════════════════════
    #  7. UTILITAIRE — découpage de texte en lignes
    # ═════════════════════════════════════════════════════════════════════════

    def _decouper_texte(self, texte, largeur_max):
        """Découpe le texte en lignes en respectant la largeur maximale.

        Algorithme greedy : on ajoute les mots un par un, et on passe à
        une nouvelle ligne quand le suivant ferait dépasser largeur_max."""

        mots   = texte.split(' ')
        lignes = []
        ligne  = ""

        for mot in mots:
            test = (ligne + " " + mot).strip()
            # Si ajouter ce mot ferait dépasser la largeur max…
            if self._police_texte.size(test)[0] > largeur_max:
                # …on commit la ligne courante et on commence une nouvelle.
                if ligne:
                    lignes.append(ligne)
                ligne = mot
            else:
                ligne = test

        # Ne pas oublier la dernière ligne (qui n'a pas déclenché de retour)
        if ligne:
            lignes.append(ligne)

        return lignes
