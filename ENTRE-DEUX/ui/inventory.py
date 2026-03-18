# ─────────────────────────────────────────
#  ENTRE-DEUX — Inventaire (la Cape + les Lueurs)
# ─────────────────────────────────────────

import pygame
from settings import *
from utils import find_file


class InventoryItem:
    def __init__(self, name, image):
        self.name = name
        self.image = image


class Inventory:
    def __init__(self):
        self.inventory_slots = [None] * 30  # 30 emplacements
        self.slot_size = 64 # taille des slots
        self.slot_margin = 10 # marge entre les slots
        self.open = False 
        self.dragging_index = None 
        self.dragging_item = None
        self.dragging_pos = (0, 0)
        self.slot_rects = [None] * len(self.inventory_slots)

        pomme = pygame.image.load(find_file("pomme.png")).convert_alpha()
        self.pomme_image = pygame.transform.scale(pomme, (self.slot_size - 10, self.slot_size - 10))
        self.nb_pommes = 0

    def changer_etat_fenetre(self):
        """Ouvre ou ferme l'inventaire"""
        self.open = not self.open

    def is_open(self):
        """Inventaire ouvert ou pas"""
        return self.open

    def add_item(self, item):
        """Ajoute un item à l'inventaire
        True = ajouté
        False = inventaire plein"""
        for i in range(len(self.inventory_slots)):
            if self.inventory_slots[i] is None:
                self.inventory_slots[i] = item
                return True
        return False

    def add_pomme(self):
        """ajoute une pomme à l'inventaire"""
        item = InventoryItem("Pomme", self.pomme_image)
        if self.add_item(item):
            self.nb_pommes += 1
            return True
        return False

    def remove_item(self, index):
        """Retire un item de l'inventaire à un index donné"""
        if 0 <= index < len(self.inventory_slots) and self.inventory_slots[index] is not None:
            self.inventory_slots[index] = None
            return True
        return False

    def drag_drop(self, events):
        """Gère les clics pour drag/drop dans l'inventaire."""
        dropped = False
        if not self.open or None in self.slot_rects:
            return
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self.slot_rects):
                    if rect and rect.collidepoint(event.pos): #clic sur un slot
                        if self.inventory_slots[i] is not None:
                            self.dragging_index = i #index
                            self.dragging_item = self.inventory_slots[i] #item
                            self.inventory_slots[i] = None #vide le slot
                        break

            elif event.type == pygame.MOUSEMOTION :
                if self.dragging_item is not None:
                    self.dragging_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragging_item is not None:
                placed = False
                for i, rect in enumerate(self.slot_rects):
                    if rect and rect.collidepoint(event.pos):
                        self.inventory_slots[i]= self.dragging_item
                        placed = True
                        break
                if not placed:
                    self.inventory_slots[self.dragging_index] = self.dragging_item

                self.dragging_index = None
                self.dragging_item = None

    def draw(self, screen, colonnes, lignes):
        """Affiche l'inventaire"""
        if not self.open:
            return 

        w, h = screen.get_size()
        
        inv_w = min(colonnes * self.slot_size + (colonnes + 1) * self.slot_margin, w) #colonnes + marges
        inv_h = min(lignes * self.slot_size + (lignes + 1) * self.slot_margin + 50, h) #lignes + marges + espace pour le titre
        inv_x = (w - inv_w) // 2 #centre la fenetre sur l'ecran
        inv_y = (h - inv_h) // 2 

        # fond transparent + bordure
        overlay = pygame.Surface((inv_w, inv_h), pygame.SRCALPHA) #pygame.SRCALPHA pour activer la transparence
        overlay.fill((30, 30, 40, 220)) #couleur, opacité
        pygame.draw.rect(overlay, (200, 200, 200), (0, 0, inv_w, inv_h), 2) 
        screen.blit(overlay, (inv_x, inv_y))

        # titre 
        title = pygame.font.SysFont("Consolas", 24).render("ITEMS", True, BLANC)
        screen.blit(title, (inv_x + (inv_w - title.get_width()) // 2, inv_y + 8))

        # slots
        for i in range(len(self.inventory_slots)):
            col = i % colonnes
            row = i // colonnes

            slot_x = inv_x + self.slot_margin + col * (self.slot_size + self.slot_margin) 
            slot_y = inv_y + 40 + self.slot_margin + row * (self.slot_size + self.slot_margin)

            self.slot_rects[i] = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)  #pour detecter les clics

            # change de couleur si vide ou plein
            if self.inventory_slots[i] is not None:
                slot_color = (180, 150, 80) # slot plein
                border_color = (220, 190, 100)
            else:
                slot_color = (50, 65, 90) # slot vide
                border_color = (70, 90, 120)

            pygame.draw.rect(screen, slot_color, self.slot_rects[i])
            pygame.draw.rect(screen, border_color, self.slot_rects[i], 2)

            # affiche l'item s'il est présent
            if self.inventory_slots[i] is not None:
                item_image = self.inventory_slots[i].image
                img_rect = item_image.get_rect(center=(slot_x + self.slot_size // 2, slot_y + self.slot_size // 2)) #get_rect(center=..) pour centrer l'image dans le slot
                screen.blit(item_image, img_rect)

        # drag drop
        if self.dragging_item is not None:
            drag_surface = self.dragging_item.image.copy()
            drag_surface.set_alpha(180)
            drag_rect = drag_surface.get_rect(center=self.dragging_pos)
            screen.blit(drag_surface, drag_rect)

