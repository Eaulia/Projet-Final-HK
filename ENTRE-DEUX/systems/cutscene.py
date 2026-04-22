# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Cinématiques scriptées — STUB / À COMPLÉTER
# ─────────────────────────────────────────────────────────────────────────────
#
#  ÉTAT ACTUEL : VIDE (réservé pour les futures cinématiques)
#  ----------------------------------------------------------
#  Aujourd'hui, le jeu n'a PAS de système de cinématique scriptée. Si on
#  veut un événement narratif (caméra qui se déplace seule, dialogue qui
#  se joue, fade noir → texte qui apparaît, etc.), on l'écrit ad hoc
#  dans le code de la scène concernée.
#
#  Ce fichier sera utilisé quand on voudra :
#       - centraliser le système (un Cutscene = une liste d'étapes).
#       - permettre à l'éditeur de poser des "déclencheurs" qui lancent
#         une cinématique quand le joueur entre dans une zone.
#
#  IDÉE D'ARCHITECTURE PRÉVUE
#  --------------------------
#       class Cutscene:
#           def __init__(self, steps): self.steps = steps
#           def update(self, dt): ...   # joue l'étape courante
#           def is_done(self):    ...   # True quand toutes les étapes sont faites
#
#       # Une étape = (type, paramètres) :
#       Cutscene([
#           ("camera_move",   {"to": (1500, 200), "duration": 2.0}),
#           ("show_text",     {"text": "Tu te souviens ?", "duration": 3.0}),
#           ("fade_to_black", {"duration": 1.5}),
#           ("load_scene",    {"name": "souvenir_1"}),
#       ])
#
#  Petit lexique :
#     - cinématique = séquence non-interactive (le joueur ne contrôle plus
#                     pour quelques secondes). Très utilisé pour la narration.
#     - script      = ici "scripté" = pré-écrit en dur (≠ improvisé). Une
#                     suite d'étapes connue d'avance qui se joue toujours
#                     pareil.
#     - déclencheur = zone du monde qui, quand le joueur entre dedans,
#                     lance une cinématique. Posé via l'éditeur (à venir).
#     - stub        = embryon — le fichier existe mais n'a rien dedans
#                     pour l'instant. Sa simple existence dit "ce module
#                     est prévu, gardez-lui sa place".
#
#  POURQUOI GARDER UN FICHIER VIDE ?
#  ---------------------------------
#  Pour DOCUMENTER L'INTENTION. Un nouveau venu sur le projet voit ce
#  fichier dans systems/, lit l'en-tête, et sait que les cinématiques
#  doivent venir ici (pas s'éparpiller ailleurs).
#
# ─────────────────────────────────────────────────────────────────────────────

# (Implémentation à venir — voir l'esquisse d'architecture dans le header.)
