# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Jauge de Peur (réservé / brouillon)
# ─────────────────────────────────────────────────────────────────────────────
#
#  ÉTAT ACTUEL : RÉSERVÉ (mécanique conçue, pas encore branchée au gameplay)
#  ------------------------------------------------------------------------
#  Une JAUGE qui démarre PLEINE (= peur maximale) et qui DESCEND quand le
#  joueur fait certaines actions positives (rallumer une bougie, libérer
#  un compagnon, etc.). À 0, on a vaincu la peur → événement final.
#
#  L'API est volontairement simple : reduce(), increase(), is_zero(),
#  get_ratio(). Quand on branchera la mécanique au jeu, on appellera
#  ces 4 méthodes depuis le bon endroit.
#
#  EXEMPLE D'USAGE PRÉVU
#  ---------------------
#       fear = FearSystem(max_fear=100)        # 100 = peur maximale
#       ...
#       # Le joueur ramène une lueur dans le foyer :
#       fear.reduce(15)                        # peur diminue de 15 points
#
#       # Le joueur tombe dans un piège effrayant :
#       fear.increase(10)
#
#       # Pour la jauge HUD :
#       hud_alpha = int(255 * fear.get_ratio())   # 1.0 → 0.0
#
#       # Fin de jeu / déclenchement final :
#       if fear.is_zero():
#           game.end_credits()
#
#  Petit lexique :
#     - jauge        = barre / pourcentage qui représente une valeur
#                      bornée (vie, faim, peur...). Stockée comme un
#                      simple int / float entre 0 et max.
#     - ratio        = nombre entre 0 et 1, indépendant des unités. Pratique
#                      pour le HUD (largeur de barre = ratio × largeur_max).
#     - clamp        = "borner" un nombre dans [min, max]. Ici via les
#                      max(0, ...) et min(max_fear, ...) pour empêcher
#                      d'aller négatif ou de dépasser le plafond.
#
#  POURQUOI COMMENCER À max_fear (PEUR MAX) ?
#  ------------------------------------------
#  Le joueur découvre un monde HOSTILE. La jauge à fond renforce le ton
#  initial. Chaque action positive l'amenuise, ce qui crée un objectif
#  visuel clair sans dialogue ni tutoriel.
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  PAS ENCORE. Quand on branchera la mécanique :
#       core/game.py instanciera self.fear = FearSystem()
#       ui/hud.py affichera la jauge
#       certaines actions du joueur appelleront fear.reduce() / increase()
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D22]  ratio dans [0, 1] — indépendant du max, pratique pour le HUD
#
# ─────────────────────────────────────────────────────────────────────────────


class FearSystem:
    """Jauge de Peur. Démarre pleine et diminue quand le joueur progresse."""

    def __init__(self, max_fear=100):
        self.max_fear = max_fear
        self.current  = max_fear           # commence à fond (= peur maximale)

    def reduce(self, amount):
        """Diminue la peur de `amount`, en restant ≥ 0."""
        self.current = max(0, self.current - amount)

    def increase(self, amount):
        """Augmente la peur de `amount`, en restant ≤ max_fear."""
        self.current = min(self.max_fear, self.current + amount)

    def is_zero(self):
        """True quand la peur est totalement vaincue → événement final."""
        return self.current <= 0

    def get_ratio(self):
        """Renvoie un float entre 0 et 1 (pratique pour la jauge HUD)."""
        return self.current / self.max_fear
