# utils.py — Fonctions utilitaires
import os
import pygame
import settings


def find_file(filename, search_dir="assets"):
    """
    Cherche un fichier par son nom dans tout le dossier assets.
    Retourne le chemin complet absolu.
    
    Exemple : find_file("player_idle.png") 
    → "/Users/juliou/ENTRE-DEUX/assets/images/player_idle.png"
    """
    base = os.path.dirname(os.path.abspath(__file__))  # Dossier racine du projet
    search_path = os.path.join(base, search_dir)

    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)

    raise FileNotFoundError(f"Fichier '{filename}' introuvable dans '{search_dir}'")


def draw_mouse_coords(surf, camera=None):
    """
    Affiche les coordonnées de la souris en haut à gauche.
    Si camera est fournie, affiche aussi les coords dans le monde.
    """
    font = pygame.font.SysFont("Arial", 18)
    mx, my = pygame.mouse.get_pos()

    # Coordonnées écran
    text_screen = font.render(f"Ecran  x:{mx}  y:{my}", True, (255, 255, 0))
    surf.blit(text_screen, (10, 10))

    # Coordonnées monde (avec la caméra)
    if camera:
        wx = settings.wx = int(mx + camera.offset_x)
        wy = settings.wy = int(my + camera.offset_y)
        text_world = font.render(f"Monde  x:{wx}  y:{wy}", True, (0, 255, 180))
        surf.blit(text_world, (10, 30))