# ─────────────────────────────────────────
#  ENTRE-DEUX — Boîte de dialogue
# ─────────────────────────────────────────
#
#  Style Undertale : texte lettre par lettre, son par caractère,
#  indicateur ▼ clignotant quand la ligne est terminée.
#
#  Utilisation :
#    boite.demarrer([("Bonjour !", "Nimbus"), ("...", "Nimbus")])
#    boite.update(dt)       ← chaque frame
#    boite.draw(surf)       ← chaque frame
#    boite.avancer()        ← quand le joueur appuie sur Espace/Entrée

import math
import struct
import pygame


class BoiteDialogue:

    VITESSE_LETTRE  = 0.034   # secondes entre deux lettres
    COULEUR_FOND    = (12, 12, 24, 218)
    COULEUR_BORD    = (170, 150, 255)
    COULEUR_TEXTE   = (235, 235, 235)
    COULEUR_ORATEUR = (255, 215, 80)   # doré, comme dans HK
    HAUTEUR_BOITE   = 155

    def __init__(self):
        self.actif  = False

        self._lignes         = []    # [(texte, orateur), ...]
        self._index          = 0     # ligne en cours
        self._nb_car         = 0     # nb de caractères révélés
        self._timer_lettre   = 0.0
        self._tout_affiche   = False

        self._phase_cligno   = 0.0   # pour l'animation du ▼
        self._son_bip        = None  # généré à la première utilisation

        self._police_orateur = None
        self._police_texte   = None

    # ── Initialisation lazy ───────────────────────────────────────────────

    def _init_polices(self):
        if self._police_orateur is None:
            self._police_orateur = pygame.font.SysFont("Consolas", 17, bold=True)
            self._police_texte   = pygame.font.SysFont("Consolas", 16)

    def _init_son(self):
        """
        Génère un bip court directement en mémoire — pas besoin de fichier audio.
        Fréquence et durée choisies pour imiter le son de dialogue d'Undertale.
        """
        if self._son_bip is not None:
            return

        try:
            freq_mix  = pygame.mixer.get_init()[0]
            frequence = 860      # Hz — légèrement métallique
            duree     = 0.038    # secondes
            volume    = 0.20

            nb_samples = int(freq_mix * duree)
            donnees    = bytearray()

            for i in range(nb_samples):
                # Envelope douce pour éviter le clic au début et à la fin
                env = min(1.0, min(i, nb_samples - i) / max(1, int(freq_mix * 0.007)))
                val = int(volume * 32767 * env * math.sin(2 * math.pi * frequence * i / freq_mix))
                val = max(-32768, min(32767, val))
                echantillon = struct.pack('<h', val)
                donnees += echantillon + echantillon   # stéréo (L + R identiques)

            self._son_bip = pygame.mixer.Sound(buffer=bytes(donnees))

        except Exception:
            pass   # le jeu tourne silencieusement si le mixer n'est pas dispo

    # ── API publique ──────────────────────────────────────────────────────

    def demarrer(self, lignes):
        """
        Démarre un dialogue.

        lignes : liste de tuples (texte, orateur)  ou  liste de strings simples.

        Exemple :
            boite.demarrer([
                ("Tu es tombé de bien haut.", "Nimbus"),
                ("...", "Nimbus"),
            ])
        """
        self._lignes = []
        for ligne in lignes:
            if isinstance(ligne, str):
                self._lignes.append((ligne, ""))
            else:
                self._lignes.append(tuple(ligne))

        self._index        = 0
        self._nb_car       = 0
        self._timer_lettre = 0.0
        self._tout_affiche = False
        self._phase_cligno = 0.0
        self.actif         = True

    def avancer(self):
        """
        Appelé quand le joueur appuie sur Espace ou Entrée.

        - Si la ligne n'est pas encore finie → affiche tout d'un coup.
        - Si la ligne est finie → passe à la suivante (ou ferme la boîte).
        """
        if not self.actif:
            return

        if not self._tout_affiche:
            # Révèle tout le texte instantanément
            self._nb_car       = len(self._lignes[self._index][0])
            self._tout_affiche = True
        else:
            self._index += 1
            if self._index >= len(self._lignes):
                self.actif = False
            else:
                self._nb_car       = 0
                self._timer_lettre = 0.0
                self._tout_affiche = False

    def update(self, dt):
        if not self.actif:
            return

        # Animation du ▼ (clignotant continu)
        self._phase_cligno += dt * 4.0

        if self._tout_affiche:
            return

        # Avance lettre par lettre
        self._init_son()
        texte = self._lignes[self._index][0]
        self._timer_lettre += dt

        while self._timer_lettre >= self.VITESSE_LETTRE and self._nb_car < len(texte):
            self._timer_lettre -= self.VITESSE_LETTRE
            self._nb_car += 1

            # Bip uniquement sur les caractères visibles (pas les espaces)
            if texte[self._nb_car - 1] not in (' ', '\n') and self._son_bip:
                self._son_bip.play()

        if self._nb_car >= len(texte):
            self._tout_affiche = True

    # ── Rendu ─────────────────────────────────────────────────────────────

    def draw(self, surf):
        if not self.actif:
            return

        self._init_polices()
        w, h    = surf.get_size()
        marge   = 28
        bx      = marge
        by      = h - self.HAUTEUR_BOITE - marge
        bw      = w - marge * 2
        bh      = self.HAUTEUR_BOITE

        # Fond semi-transparent
        fond = pygame.Surface((bw, bh), pygame.SRCALPHA)
        fond.fill(self.COULEUR_FOND)
        surf.blit(fond, (bx, by))

        # Bordure extérieure + intérieure
        pygame.draw.rect(surf, self.COULEUR_BORD, (bx, by, bw, bh), 2)
        pygame.draw.rect(surf, (60, 50, 110), (bx + 4, by + 4, bw - 8, bh - 8), 1)

        texte, orateur = self._lignes[self._index]

        # Nom de l'orateur (en doré, en haut à gauche)
        y_texte = by + 16
        if orateur:
            nom_surf = self._police_orateur.render(orateur, True, self.COULEUR_ORATEUR)
            surf.blit(nom_surf, (bx + 14, y_texte))
            y_texte += 28
            # Petite ligne sous le nom
            pygame.draw.line(surf, (80, 65, 140),
                             (bx + 14, y_texte - 4),
                             (bx + 14 + nom_surf.get_width() + 20, y_texte - 4), 1)

        # Texte révélé jusqu'à _nb_car, avec retour à la ligne automatique
        texte_visible = texte[:self._nb_car]
        largeur_max   = bw - 30

        lignes_rendues = self._decouper_texte(texte_visible, largeur_max)

        for i, ligne in enumerate(lignes_rendues[:4]):   # max 4 lignes visibles
            txt_surf = self._police_texte.render(ligne, True, self.COULEUR_TEXTE)
            surf.blit(txt_surf, (bx + 14, y_texte + i * 24))

        # Indicateur ▼ clignotant quand tout est affiché
        if self._tout_affiche:
            alpha    = int(200 + 55 * math.sin(self._phase_cligno))
            tri_surf = self._police_texte.render("▼", True, (alpha, alpha, alpha))
            surf.blit(tri_surf, (bx + bw - 26, by + bh - 26))

    def _decouper_texte(self, texte, largeur_max):
        """Découpe le texte en lignes en respectant la largeur maximale."""
        mots   = texte.split(' ')
        lignes = []
        ligne  = ""

        for mot in mots:
            test = (ligne + " " + mot).strip()
            if self._police_texte.size(test)[0] > largeur_max:
                if ligne:
                    lignes.append(ligne)
                ligne = mot
            else:
                ligne = test

        if ligne:
            lignes.append(ligne)

        return lignes
