# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Game Feel / "Juice"
# ─────────────────────────────────────────────────────────────────────────────
#
#  À QUOI SERT CE FICHIER ?
#  ------------------------
#  Le mot "juice" (ou "game feel") en game dev désigne ces petits effets qui
#  ne CHANGENT RIEN au gameplay, mais font passer un jeu de "fonctionnel" à
#  "satisfaisant à jouer". Concrètement ici, deux effets minimalistes :
#
#       1) ScreenShake — la caméra TREMBLE pendant 0,2s à un impact fort.
#                        → Tu sens le coup, alors qu'au fond rien n'a bougé
#                          dans le monde.
#
#       2) HitPause    — la simulation se FIGE pendant ~80 ms à un coup réussi.
#                        → "Oui je l'ai touché, là, MAINTENANT." C'est un
#                          accent musical posé sur l'action.
#
#  EXEMPLE CONCRET (combo des deux à un coup d'épée qui touche)
#  ------------------------------------------------------------
#       1) Le joueur tape, l'attaque touche un ennemi.
#       2) On déclenche :
#               shake.trigger(amplitude=6, duree=0.2)
#               pause.trigger(0.08)
#       3) Pendant 80 ms, le rendu continue mais le `dt` envoyé à la
#          physique est ZÉRO → tout est figé, le joueur sent l'impact.
#       4) Pendant 200 ms, la caméra se balade aléatoirement dans
#          un rayon de ±6 px qui décroît jusqu'à 0.
#       5) Tout repart normalement. Total : 0,2s. Sans ces effets,
#          le coup paraîtrait "mou".
#
#  Petit lexique :
#     - juice / game feel = ressenti micro du jeu (poids des coups, vivacité
#                           des contrôles, retour visuel/sonore des actions).
#                           Notion popularisée par la conf "Juice it or lose it".
#     - screen shake      = "tremblement d'écran". On décale temporairement
#                           toute la vue de quelques pixels.
#     - hit pause         = "pause au coup". Très court gel de la simulation
#                           quand un coup porte. Très courant en JRPG / action.
#     - amplitude         = ici, le NOMBRE DE PIXELS max dont la caméra peut
#                           se décaler à un instant donné.
#     - décroissance      = "qui diminue dans le temps". Le shake démarre fort
#                           et s'atténue jusqu'à 0 → on évite l'effet sismique
#                           qui donne mal au cœur.
#     - dt                = "delta time" = temps écoulé depuis la frame
#                           précédente, en secondes. La physique multiplie
#                           toutes ses vitesses par dt → si on met dt=0,
#                           rien ne bouge → freeze.
#     - offset            = "décalage". La caméra ajoute (dx, dy) à la
#                           position de l'image avant de l'afficher. shake
#                           renvoie justement (dx, dy).
#
#  POURQUOI "LE PLUS FORT GAGNE" SUR LES TRIGGERS SUCCESSIFS ?
#  -----------------------------------------------------------
#  Si trois ennemis explosent en même temps, on ne veut pas additionner
#  leurs shakes (→ caméra qui part dans le décor). On garde simplement
#  le plus violent : le ressenti reste fort sans devenir n'importe quoi.
#
#  POURQUOI HITPAUSE NE TOUCHE PAS AU RENDU ?
#  ------------------------------------------
#  Si on figeait aussi le rendu, l'écran se gèlerait littéralement
#  pendant 80 ms → ça ressemblerait à un freeze technique, pas à un
#  effet voulu. En ne figeant QUE la physique (dt = 0), le rendu
#  continue à 60 fps : visuellement on voit un instantané "vivant"
#  mais immobile. C'est ÇA, l'accent voulu.
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  core/game.py instancie un ScreenShake et un HitPause, les déclenche
#  aux impacts (combat, dégâts encaissés), et applique l'offset à la
#  caméra dans la boucle de rendu.
#
#  JE VEUX MODIFIER QUOI ?
#  -----------------------
#     - Tremblement plus / moins fort      → arg `amplitude` de trigger()
#     - Tremblement plus / moins long      → arg `duree` de trigger()
#     - Freeze plus / moins long           → arg `duree` de pause.trigger()
#     - Désactiver pour réglages "calmes"  → ne pas appeler trigger() du tout
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D8]   dt           — temps inter-frames, base de la physique
#     [D22]  états        — la classe garde "combien de temps il me reste"
#
# ─────────────────────────────────────────────────────────────────────────────

import random


# ═════════════════════════════════════════════════════════════════════════════
#  1. SCREEN SHAKE — la caméra tremble brièvement
# ═════════════════════════════════════════════════════════════════════════════

class ScreenShake:
    """Tremblement de caméra. La caméra demande l'offset à chaque frame."""

    def __init__(self):
        self.amplitude = 0.0       # px max de décalage (au plus fort)
        self.duree     = 0.0       # durée totale du shake en secondes
        self.time_left = 0.0       # temps restant
        self._offset   = (0, 0)    # dernier (dx, dy) calculé

    def trigger(self, amplitude=6, duree=0.2):
        """Démarre un shake. Si un autre est déjà en cours, on garde le
        plus fort (pas de cumul → cf. encart du header)."""
        if amplitude > self.amplitude or self.time_left <= 0:
            self.amplitude = amplitude
            self.duree     = duree
            self.time_left = duree

    def update(self, dt):
        """À appeler chaque frame. Renvoie (dx, dy) à appliquer à la caméra.

        Quand time_left = duree → ratio = 1 → amplitude pleine.
        Quand time_left = 0    → ratio = 0 → amplitude nulle (fin du shake).
        Entre les deux → décroissance LINÉAIRE (= simple, suffit largement).
        """
        if self.time_left <= 0:
            self._offset = (0, 0)
            return self._offset

        self.time_left -= dt
        # max(0.001, ...) = sécurité division par zéro si quelqu'un déclenche
        # avec duree=0 par mégarde.
        ratio = max(0.0, self.time_left / max(0.001, self.duree))
        amp   = self.amplitude * ratio

        # Décalage aléatoire dans un carré [-amp, +amp] x [-amp, +amp].
        # random.uniform = "tire un float n'importe où entre les deux bornes".
        self._offset = (
            random.uniform(-amp, amp),
            random.uniform(-amp, amp),
        )
        if self.time_left <= 0:
            self._offset = (0, 0)
        return self._offset

    @property
    def offset(self):
        """Lecture du dernier offset SANS faire avancer le temps. Utile
        si la caméra veut juste consulter sans re-tirer un nombre aléatoire."""
        return self._offset


# ═════════════════════════════════════════════════════════════════════════════
#  2. HIT-PAUSE — freeze ultra-court de la physique à l'impact
# ═════════════════════════════════════════════════════════════════════════════

class HitPause:
    """Bloque la simulation pendant 50–100 ms. Le RENDU continue, c'est
    seulement le `dt` envoyé à la physique qu'on met à zéro pendant ce
    temps. Effet : impact "claqué" très satisfaisant."""

    def __init__(self):
        self.time_left = 0.0

    def trigger(self, duree=0.06):
        """Démarre (ou prolonge) un freeze. Si déjà en cours, on garde le
        plus long des deux : un freeze plus long ne doit pas être
        raccourci par un freeze plus court qui arrive après."""
        self.time_left = max(self.time_left, duree)

    def is_active(self):
        """True tant que le freeze n'est pas terminé. game.py l'utilise
        pour décider si elle envoie dt=0 à la physique."""
        return self.time_left > 0

    def tick(self, dt):
        """Décrémente le temps restant. Appelé chaque frame avec le
        VRAI dt (pas le dt mis à zéro pour la physique), sinon le freeze
        ne s'arrêterait jamais."""
        if self.time_left > 0:
            self.time_left -= dt
            if self.time_left < 0:
                self.time_left = 0
