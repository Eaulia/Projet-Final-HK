# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — SceneManager (multi-zones) — STUB / EMBRYON
# ─────────────────────────────────────────────────────────────────────────────
#
#  ÉTAT ACTUEL : EMBRYON (pas encore branché au jeu)
#  -------------------------------------------------
#  Compagnon de world/scene.py (cf. son header pour le contexte). Cette
#  classe servira à GÉRER PLUSIEURS SCÈNES et passer de l'une à l'autre.
#
#  Aujourd'hui, le jeu n'a qu'UNE scène à la fois (chargée depuis JSON
#  par world/editor.py). Quand on voudra plusieurs cartes connectées
#  par des portes / transitions, on pourra utiliser ça.
#
#  USAGE PRÉVU
#  -----------
#       sm = SceneManager()
#       sm.add_scene("foret",  Scene("foret"))
#       sm.add_scene("donjon", Scene("donjon"))
#
#       sm.load("foret")              # active la forêt
#       sm.update(dt, joueur)         # update la scène active
#       sm.draw(screen)               # dessine la scène active
#
#       # Plus tard, joueur entre dans le donjon :
#       sm.load("donjon")             # bascule
#
#  Petit lexique :
#     - scène active   = la seule scène update/dessinée à un instant donné.
#                        Les autres "dorment" en mémoire (rapide à recharger).
#     - registre       = self.scenes est un dict {nom: Scene} = un annuaire.
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D22]  conventions update/draw — méthodes alignées sur le reste du jeu
#
# ─────────────────────────────────────────────────────────────────────────────


class SceneManager:
    """Gère un ensemble de scènes et bascule de l'une à l'autre — STUB."""

    def __init__(self):
        self.scenes  = {}     # {nom: Scene}
        self.current = None   # Scene active (None si rien chargé)

    def add_scene(self, name, scene):
        """Enregistre une scène sous un nom. Ne l'active pas (cf. load())."""
        self.scenes[name] = scene

    def load(self, name):
        """Active la scène `name` si elle existe (silencieux sinon)."""
        if name in self.scenes:
            self.current = self.scenes[name]

    def update(self, dt, player):
        """Update la scène active. Sans scène active → rien à faire."""
        if self.current:
            self.current.update(dt, player)

    def draw(self, surf):
        """Dessine la scène active. Sans scène active → rien à dessiner."""
        if self.current:
            self.current.draw(surf)
