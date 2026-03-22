# ─────────────────────────────────────────
#  ENTRE-DEUX — Gestionnaire d'états
# ─────────────────────────────────────────

MENU      = "menu"
GAME      = "game"
PAUSE     = "pause"
GAME_OVER = "game_over"


class StateManager:
    def __init__(self):
        self.state = MENU

    def switch(self, new_state):
        self.state = new_state

    @property
    def is_menu(self):      return self.state == MENU

    @property
    def is_game(self):      return self.state == GAME

    @property
    def is_paused(self):    return self.state == PAUSE

    @property
    def is_game_over(self): return self.state == GAME_OVER
