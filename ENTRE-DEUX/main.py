# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Point d'entrée du jeu
# ─────────────────────────────────────────────────────────────────────────────
#
#  À QUOI SERT CE FICHIER ?
#  ------------------------
#  C'est LE fichier qu'on lance pour démarrer le jeu :
#
#       py main.py
#
#  Tout le code utile vit ailleurs (core/game.py, entities/, ui/, ...).
#  Ce fichier ne fait QUE 2 choses :
#       1) Importer la classe Game.
#       2) Si on est lancé directement → créer une instance et appeler run().
#
#  C'EST QUOI `if __name__ == "__main__"` ?
#  -----------------------------------------
#  C'est une PROTECTION. Quand Python exécute un fichier directement
#  (`py main.py`), il met la variable spéciale `__name__` à `"__main__"`.
#  Quand on IMPORTE ce fichier depuis ailleurs (`import main`), Python met
#  `__name__` au nom du module (`"main"`).
#
#  Donc :
#       py main.py            → __name__ == "__main__"  → on entre dans le if
#                                                          → le jeu démarre
#       import main           → __name__ == "main"      → on n'entre PAS dans
#                                                          le if → rien ne démarre
#
#  Du coup, on peut importer main.py sans risquer de lancer le jeu par
#  erreur (utile pour les tests, ou pour qu'un autre script utilise une
#  fonction d'ici sans tout démarrer).
#
#  POURQUOI MAIN.PY EST AUSSI COURT ?
#  ----------------------------------
#  Convention universelle Python : main.py = un point d'entrée minimal
#  qui DÉLÈGUE tout à un module / une classe métier. Avantages :
#       - lecture immédiate "qu'est-ce qui démarre ?"
#       - facile à remplacer par un autre point d'entrée (ex : tests)
#       - pas de logique cachée dans un fichier qu'on ne lit jamais
#
#  Petit lexique :
#     - point d'entrée   = LE fichier qu'on lance pour démarrer un programme.
#     - __name__         = variable spéciale Python remplie automatiquement.
#                          "__main__" si lancé directement, sinon le nom du module.
#     - if __name__ ...  = formule idiomatique de protection.
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D1]  point d'entrée — convention Python pour démarrer une appli
#
# ─────────────────────────────────────────────────────────────────────────────

from core.game import Game


if __name__ == "__main__":
    game = Game()
    game.run()
