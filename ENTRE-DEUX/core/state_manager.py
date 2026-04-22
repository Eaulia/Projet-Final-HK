# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Gestionnaire d'état du jeu
# ─────────────────────────────────────────────────────────────────────────────
#
#  À QUOI SERT CE FICHIER ?
#  ------------------------
#  À tout moment, le jeu est dans UN état (un seul) parmi :
#       MENU      → on est dans le menu principal
#       GAME      → on joue
#       PAUSE     → on a appuyé sur Échap pendant le jeu
#       GAME_OVER → on est mort
#
#  Cette classe garde l'état actuel et fournit des raccourcis pour le
#  TESTER (is_menu, is_game, is_paused, is_game_over). Le jeu lit ces
#  flags pour décider quoi dessiner / quoi mettre à jour à chaque frame.
#
#  EXEMPLE CONCRET (boucle simplifiée du jeu)
#  ------------------------------------------
#       state = StateManager()
#       ...
#       while running:
#           if state.is_menu:
#               menu.update_and_draw()
#               if menu.start_pressed:
#                   state.switch(GAME)
#           elif state.is_game:
#               game.update(dt)
#               game.draw()
#           elif state.is_paused:
#               game.draw()         # on dessine le jeu figé
#               pause_overlay.draw()
#           elif state.is_game_over:
#               game_over_screen.draw()
#
#  Petit lexique :
#     - état (state) = "dans quoi le jeu est en ce moment". Concept central
#                      des "machines à états" — la structure principale qui
#                      organise un jeu.
#     - constantes   = MENU, GAME, etc. = strings prédéfinies. On utilise
#                      des constantes plutôt que d'écrire "menu" en dur
#                      partout : si on faute de frappe quelque part
#                      (`"meun"`), on s'en aperçoit AU bug, alors qu'avec
#                      la constante MENU une faute de frappe lève une
#                      NameError tout de suite.
#     - @property    = transforme une méthode en attribut. Ici on écrit
#                      `state.is_menu` (sans parenthèses) au lieu de
#                      `state.is_menu()`. Plus naturel à lire.
#     - switch       = "basculer". Méthode unique pour changer d'état.
#                      Centralisé → si on veut un jour journaliser
#                      les transitions ("MENU → GAME"), un seul endroit
#                      à modifier.
#
#  POURQUOI 4 PROPRIÉTÉS PLUTÔT QUE state == GAME PARTOUT ?
#  --------------------------------------------------------
#  Lisibilité. `if state.is_paused:` se lit comme une phrase. Et si un
#  jour on ajoute des sous-états ("inventory_open" qui équivaut à pause),
#  on peut le faire évoluer dans la propriété sans toucher tous les sites
#  d'appel.
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  core/game.py crée le StateManager au démarrage et le consulte à chaque
#  frame de la boucle principale.
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D22]  machine à états — structure pour organiser les phases d'un programme
#
# ─────────────────────────────────────────────────────────────────────────────


# ═════════════════════════════════════════════════════════════════════════════
#  CONSTANTES D'ÉTAT
# ═════════════════════════════════════════════════════════════════════════════

MENU      = "menu"
GAME      = "game"
PAUSE     = "pause"
GAME_OVER = "game_over"


# ═════════════════════════════════════════════════════════════════════════════
#  LA CLASSE
# ═════════════════════════════════════════════════════════════════════════════

class StateManager:
    """Garde l'état courant du jeu et expose des raccourcis de test."""

    def __init__(self):
        self.state = MENU                     # on démarre toujours sur le menu

    def switch(self, new_state):
        """Change l'état. Centralise les transitions (cf. encart switch dans le header)."""
        self.state = new_state

    # ─── Raccourcis de test (lisibilité) ───────────────────────────────────

    @property
    def is_menu(self):      return self.state == MENU

    @property
    def is_game(self):      return self.state == GAME

    @property
    def is_paused(self):    return self.state == PAUSE

    @property
    def is_game_over(self): return self.state == GAME_OVER
