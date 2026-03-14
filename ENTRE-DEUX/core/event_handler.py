# ─────────────────────────────────────────
#  ENTRE-DEUX — Gestion des inputs
# ─────────────────────────────────────────
# À compléter : lecture clavier/souris centralisée
import pygame 
import settings
pygame.joystick.init()
def man_on():
    if pygame.joystick.get_count() > 0:
                settings.manette = pygame.joystick.Joystick(0)  # 0 = première manette
                settings.manette.init()
                
def x_y_man():
    if settings.manette is None:
        settings.axis_x = 0
        settings.axis_y = 0
        return
    settings.axis_x = settings.manette.get_axis(0)  # gauche/droite
    settings.axis_y = settings.manette.get_axis(1)  # haut/bas