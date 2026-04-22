# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Manette / Joystick (gestion partielle des inputs)
# ─────────────────────────────────────────────────────────────────────────────
#
#  ÉTAT ACTUEL : MINIMAL
#  ---------------------
#  Ce fichier ne fait QUE la partie "manette" — détecter une manette
#  branchée et lire ses axes gauche/droite et haut/bas.
#  Le clavier et les boutons sont lus DIRECTEMENT par les autres fichiers
#  (entities/player.py, ui/menu.py...) via pygame.key.get_pressed().
#
#  À TERME on voudra centraliser TOUTES les entrées ici (clavier + manette
#  + remappage de touches), mais ce n'est pas fait. Pour l'instant, on
#  garde juste la couche manette.
#
#  EXEMPLE CONCRET
#  ---------------
#       # Au démarrage du jeu :
#       man_on()                       # détecte la manette si présente
#
#       # À chaque frame :
#       x_y_man()                      # met à jour settings.axis_x / axis_y
#       if settings.axis_x > 0.5:
#           joueur.aller_droite()
#
#  Petit lexique :
#     - joystick     = nom générique pygame pour "manette de jeu"
#                      (contrôleur Xbox, PS, générique...).
#     - axis         = un AXE analogique = nombre entre -1 et +1 selon la
#                      position du stick. axe 0 = horizontal du stick gauche,
#                      axe 1 = vertical du stick gauche.
#                      0 quand on lâche le stick (au repos).
#     - dead zone    = "zone morte" — petit voisinage de 0 où on considère
#                      que le stick est au repos (les sticks ont du jeu et
#                      renvoient ~0.05 même au repos). Le seuil est testé
#                      par les CONSOMMATEURS (ex : if axis_x > DEAD_ZONE).
#     - settings.manette = la manette est stockée dans settings (variable
#                      module) parce que plusieurs fichiers en ont besoin
#                      (joueur, menu, éditeur). Variable globale = un seul
#                      point de vérité.
#     - settings.axis_x / axis_y = idem, mises à jour ici, lues partout.
#
#  POURQUOI man_on() AVEC pygame.joystick.get_count() ?
#  ----------------------------------------------------
#  La manette est OPTIONNELLE. Si l'utilisateur n'en a pas, on ne crashe
#  pas, on laisse simplement settings.manette à None. Le reste du jeu
#  vérifie ce None avant utilisation. Avec une manette branchée :
#  on prend la 1ʳᵉ trouvée (index 0).
#
#  POURQUOI x_y_man() RÉCRIT À 0 SI PAS DE MANETTE ?
#  -------------------------------------------------
#  Si on ne touche pas à settings.axis_x quand la manette est absente,
#  on garde une vieille valeur résiduelle (qui pourrait faire bouger le
#  joueur à l'infini si elle vaut 0.7). Mettre à 0 garantit "pas de
#  manette = pas d'input manette".
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  core/game.py appelle man_on() au démarrage et x_y_man() chaque frame.
#  entities/player.py lit ensuite settings.axis_x / axis_y pour le mouvement.
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D24]  module avec état partagé — settings est ce module global
#
# ─────────────────────────────────────────────────────────────────────────────

import pygame
import settings

pygame.joystick.init()


def man_on():
    """Détecte une manette branchée et l'enregistre dans settings.manette.

    Pas de manette → settings.manette reste à None (ne plante pas)."""
    if pygame.joystick.get_count() > 0:
        settings.manette = pygame.joystick.Joystick(0)   # 0 = première manette
        settings.manette.init()


def x_y_man():
    """Lit les axes du stick gauche et stocke dans settings.axis_x / axis_y.

    Pas de manette → on force à 0 (cf. encart dans le header)."""
    if settings.manette is None:
        settings.axis_x = 0
        settings.axis_y = 0
        return
    settings.axis_x = settings.manette.get_axis(0)   # gauche/droite
    settings.axis_y = settings.manette.get_axis(1)   # haut/bas
