# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Grille spatiale (collisions rapides)
# ─────────────────────────────────────────────────────────────────────────────
#
#  À QUOI SERT CE FICHIER ?
#  ------------------------
#  Tester les collisions du joueur contre TOUTES les plateformes du niveau,
#  c'est lent. À 200 plateformes × 60 frames/s = 12 000 tests par seconde.
#  Sur une grosse map, ça grimpe vite et le jeu rame.
#
#  ASTUCE : on découpe le monde en CARRÉS (cellules) et on range chaque
#  plateforme dans les cellules qu'elle touche. Quand on cherche les
#  plateformes proches du joueur, on ne regarde QUE les cellules autour
#  de lui → 3-4 plateformes au lieu de 200.
#
#  EXEMPLE CONCRET (cellules de 128 px)
#  ------------------------------------
#       Le joueur est à x=300, y=400. Sa cellule est (2, 3) : 300 // 128 = 2.
#       Sa hitbox déborde un peu sur la cellule voisine → on regarde (2,3),
#       (3,3), peut-être (2,4) et (3,4). Total : 4 cellules.
#       Si chaque cellule contient 1-2 plateformes, on teste 4-8 collisions
#       au lieu des 200 du monde entier. ÉNORME différence.
#
#  ASCII : monde divisé en cellules de 128px
#  ┌─────┬─────┬─────┬─────┐
#  │     │     │     │     │
#  ├─────┼─────┼─────┼─────┤   La plateforme X touche 2 cellules
#  │     │  X X│X    │     │   → on l'enregistre dans LES DEUX.
#  ├─────┼─────┼─────┼─────┤   Quand on query autour du joueur,
#  │     │     │  J  │     │   on récupère les plateformes via les
#  └─────┴─────┴─────┴─────┘   cellules qui chevauchent sa hitbox.
#
#  Petit lexique :
#     - grille spatiale = "Spatial Hash Grid" en anglais. Une des structures
#                         d'accélération les plus simples pour les collisions
#                         2D. Performante quand les objets sont à peu près
#                         de la même taille (cas typique d'un platformer).
#     - cellule         = un carré de la grille. Ici, 128×128 px par défaut.
#     - cell_size       = la taille du carré. Trop PETIT → beaucoup de
#                         cellules à scanner. Trop GRAND → chaque cellule
#                         contient trop d'objets → on perd l'intérêt.
#                         128 est un bon compromis pour ce jeu.
#     - bucket          = autre nom pour "cellule" (vu en littérature anglaise).
#                         Comme un panier où on met les objets de la zone.
#     - dict {(x, y): [obj, ...]} : on indexe par tuple de coordonnées de
#                         cellule. Pratique : pas besoin de tableau 2D
#                         dimensionné à l'avance, ça grandit à la demande.
#     - setdefault      = méthode dict pratique : "renvoie la valeur pour
#                         cette clé ; si elle n'existe pas, crée-la avec
#                         cette valeur par défaut". Évite un test if/else.
#     - broad-phase     = "phase grossière" — étape qui élimine vite les
#                         non-candidats. C'est ce que fait query() :
#                         renvoie les objets qui POURRAIENT toucher.
#                         La VRAIE collision (precise) est faite ensuite
#                         par world/collision.py.
#     - rebuild         = "reconstruire". Si une plateforme bouge, ses
#                         cellules d'origine sont périmées. Pour rester
#                         simple, on jette tout et on reconstruit, plutôt
#                         que de gérer les insertions/retraits.
#
#  POURQUOI rebuild() PLUTÔT QU'UN UPDATE INCRÉMENTAL ?
#  ----------------------------------------------------
#  Dans LIMINAL, les plateformes sont QUASI STATIQUES (elles ne bougent
#  que dans l'éditeur). On reconstruit la grille seulement quand on
#  modifie le niveau, donc le coût est nul en jeu. Si un jour on a des
#  plateformes mobiles (ascenseurs), on devra passer à un update().
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  core/game.py : self.spatial_grid = SpatialGrid()
#                 self.spatial_grid.rebuild(self.scene.platforms)
#  world/collision.py : appliquer_plateformes() appelle .query() pour
#                       trouver les plateformes proches du joueur.
#
#  JE VEUX MODIFIER QUOI ?
#  -----------------------
#     - Cellules plus / moins fines → cell_size dans __init__
#     - Stocker les ENNEMIS aussi   → on en crée une 2ᵉ instance pour eux
#                                     (pas besoin de mélanger : on filtre
#                                      par type au query si nécessaire)
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D4]   pygame.Rect   — l'objet doit avoir un .rect
#     [D24]  dict comme    — pas de tableau 2D : on grandit à la demande
#            grille
#
# ─────────────────────────────────────────────────────────────────────────────


class SpatialGrid:
    """Grille de hachage spatial pour accélérer les requêtes de proximité."""

    def __init__(self, cell_size=128):
        self.cell_size = cell_size
        # {(cell_x, cell_y): [obj, obj, ...]}
        # Pas de taille fixe : le dict grandit à la demande.
        self.cells = {}

    # ─────────────────────────────────────────────────────────────────────────
    #  INSERTION / NETTOYAGE
    # ─────────────────────────────────────────────────────────────────────────

    def clear(self):
        """Vide complètement la grille."""
        self.cells.clear()

    def insert(self, obj):
        """Range `obj` dans toutes les cellules que son rect chevauche.

        L'objet doit avoir un attribut `.rect` (pygame.Rect ou compatible).
        Un objet qui chevauche 4 cellules sera ENREGISTRÉ 4 FOIS — c'est
        OK, query() dédoublonne avec un set().
        """
        for cell in self._cells_for(obj.rect):
            # setdefault : si la cellule n'existe pas encore, on la crée
            # avec une liste vide, puis on append. Évite un test if/else.
            self.cells.setdefault(cell, []).append(obj)

    def rebuild(self, objects):
        """Reconstruit toute la grille depuis zéro à partir de `objects`.

        Appelée par game.py après chaque modification de la scène
        (chargement, édition). Cf. encart "rebuild vs update incrémental"
        dans le header.
        """
        self.clear()
        for obj in objects:
            self.insert(obj)

    # ─────────────────────────────────────────────────────────────────────────
    #  REQUÊTE (broad-phase)
    # ─────────────────────────────────────────────────────────────────────────

    def query(self, rect):
        """Renvoie tous les objets qui POURRAIENT toucher `rect` (broad-phase).

        On utilise un set() pour dédoublonner : si un objet est dans 4
        cellules qu'on scanne, il ne ressortira qu'une fois.

        Le VRAI test "ce rect touche-t-il vraiment l'autre rect ?" est
        fait après par l'appelant (world/collision.py).
        """
        found = set()
        for cell in self._cells_for(rect):
            for obj in self.cells.get(cell, []):
                found.add(obj)
        return found

    # ─────────────────────────────────────────────────────────────────────────
    #  CALCUL DES CELLULES TOUCHÉES PAR UN RECT
    # ─────────────────────────────────────────────────────────────────────────

    def _cells_for(self, rect):
        """Renvoie la liste des coordonnées (cell_x, cell_y) que `rect` touche.

        Astuce maths : rect.left // cell_size = numéro de cellule
                       contenant la position rect.left.
        On fait pareil pour right/top/bottom et on parcourt le rectangle
        de cellules entre les deux coins.
        """
        cs = self.cell_size
        x1 = rect.left   // cs
        y1 = rect.top    // cs
        x2 = rect.right  // cs
        y2 = rect.bottom // cs

        cells = []
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                cells.append((x, y))
        return cells
