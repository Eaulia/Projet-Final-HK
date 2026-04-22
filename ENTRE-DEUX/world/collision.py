# ─────────────────────────────────────────────────────────────────────────────
#  LIMINAL (ENTRE-DEUX) — Résolution des collisions
# ─────────────────────────────────────────────────────────────────────────────
#
#  À QUOI SERT CE FICHIER ?
#  ------------------------
#  Quand le joueur (ou un ennemi) bouge, il peut se retrouver PARTIELLEMENT
#  À L'INTÉRIEUR d'une plateforme. Ce fichier répond à la question :
#
#       "Le joueur empiète sur cette plateforme. De combien je dois le
#        repousser, et dans quelle direction ?"
#
#  L'approche est la "résolution par axe minimal de pénétration" (MTV) :
#       1) On mesure de combien le joueur est rentré DE CHAQUE CÔTÉ
#          (gauche, droite, dessus, dessous).
#       2) On le pousse dans le sens du plus PETIT enfoncement.
#       3) On annule la vitesse dans cet axe (s'il était en train de
#          tomber et qu'il atterrit → vy = 0 ; etc.).
#
#  EXEMPLE CONCRET
#  ---------------
#       Joueur (rect 16×32) tombe sur une plateforme (rect 200×8).
#       Sa bbox finit à y_bottom = 305, alors que le sol est à y_top = 300.
#                  → pénétration "dessus"  =   5 px
#                  → pénétration "dessous" = 295 px (énorme)
#                  → pénétration "gauche/droite" = grandes aussi
#       Le min est "dessus" → on remonte le joueur de 5 px et vy = 0.
#       → Atterrissage propre, le joueur se pose pile sur la plateforme.
#
#  POURQUOI mode_mur=True ?
#  ------------------------
#  Pour les MURS (collisions latérales tatillonnes), on veut :
#       - "Tu te déplaçais VERS le mur ?" → OK, on te bloque.
#       - "Tu venais d'en SORTIR ?"       → on ne te repousse PAS,
#                                           sinon on te repropulse à l'intérieur.
#  D'où le test `vx >= 0` ou `vx <= 0` selon le côté. Sur les plateformes
#  classiques on s'en moque (mode_mur=False) : on pousse toujours.
#
#  Petit lexique :
#     - hitbox       = rectangle invisible utilisé pour la collision (≠ sprite,
#                      qui est le rectangle visible). En général la hitbox
#                      est un peu plus petite que le sprite.
#     - colliderect  = méthode pygame.Rect : "ces deux rects se chevauchent ?"
#     - pénétration  = "de combien le joueur est rentré dans l'obstacle".
#                      Mesurée pour chaque côté.
#     - MTV          = "Minimum Translation Vector" — le plus petit déplacement
#                      qui sépare deux formes qui se chevauchent. Algorithme
#                      classique de collision 2D.
#     - on_ground    = booléen "le joueur a-t-il les pieds sur quelque chose ?".
#                      Mis à True ici quand on atterrit sur le DESSUS d'un obstacle.
#                      Sert pour autoriser le saut, ne pas sauter en l'air, etc.
#     - SpatialGrid  = structure (cf. systems/spatial_grid.py) qui stocke
#                      les plateformes par cases pour ne renvoyer QUE celles
#                      qui sont proches du joueur (au lieu de toutes les
#                      tester). Énorme gain de perf sur grandes maps.
#     - duck typing  = en Python : "si ça ressemble à un canard et nage
#                      comme un canard, c'est un canard". Concrètement ici,
#                      `hasattr(x, 'query')` → "si tu as la méthode query,
#                      je te traite comme une SpatialGrid".
#
#  OÙ EST-CE UTILISÉ ?
#  -------------------
#  core/game.py : à chaque frame, après le mouvement du joueur, on appelle
#       appliquer_plateformes(self.joueur, self.spatial_grid)
#  qui finit par appeler resoudre_collision() pour chaque obstacle proche.
#
#  JE VEUX MODIFIER QUOI ?
#  -----------------------
#     - Plus de souplesse dans les collisions latérales → cf. mode_mur
#     - Une plateforme TRAVERSABLE par le bas (one-way) → tester vy > 0
#       avant le bloc "atterrissage" et l'ignorer sinon
#     - Garder une partie de la vitesse au lieu de la mettre à 0
#       (rebond) → remplacer `entite.vy = 0` par `entite.vy = -vy * 0.5`
#
#  CONCEPTS (voir docs/DICTIONNAIRE.md) :
#  --------------------------------------
#     [D4]   pygame.Rect    — la pierre angulaire des collisions 2D
#     [D22]  on_ground      — état booléen lu pour autoriser le saut
#
# ─────────────────────────────────────────────────────────────────────────────


# ═════════════════════════════════════════════════════════════════════════════
#  1. RÉSOLUTION D'UNE COLLISION (entité ↔ un obstacle)
# ═════════════════════════════════════════════════════════════════════════════

def resoudre_collision(entite, rect_obstacle, mode_mur=False):
    """Pousse `entite` hors de `rect_obstacle` selon l'axe d'enfoncement minimal.

    PARAMÈTRES
    ----------
    entite        : objet avec au moins .rect, .vy, .vx, .on_ground
    rect_obstacle : pygame.Rect de la plateforme/mur
    mode_mur      : True = vérifier la direction de déplacement avant de
                    pousser sur les côtés (évite les coups d'éjection
                    parasites quand on est appuyé contre un mur).
    """

    # Pas de chevauchement → rien à faire.
    if not entite.rect.colliderect(rect_obstacle):
        return

    # ── Mesure des 4 enfoncements ────────────────────────────────────────────
    # Lecture : "de combien le côté X de l'entité dépasse le côté X opposé
    # de l'obstacle". Plus le nombre est PETIT, plus c'est ce côté qu'on
    # devra utiliser pour la résolution (= le moins de mouvement à faire).
    penetration_gauche  = entite.rect.right    - rect_obstacle.left   # entité dans le bord gauche
    penetration_droite  = rect_obstacle.right  - entite.rect.left     # entité dans le bord droit
    penetration_dessus  = entite.rect.bottom   - rect_obstacle.top    # entité dans le toit
    penetration_dessous = rect_obstacle.bottom - entite.rect.top      # entité dans le plancher

    plus_faible = min(
        penetration_gauche,
        penetration_droite,
        penetration_dessus,
        penetration_dessous,
    )

    # On lit vx/vy avec getattr pour être tolérant — toutes les "entités"
    # n'en ont pas forcément (ex : un PNJ statique).
    vy = getattr(entite, 'vy', 0)
    vx = getattr(entite, 'vx', 0)

    # ── Résolution selon l'axe gagnant ───────────────────────────────────────
    # Le test sur vy/vx évite des cas absurdes (ex : on monte → on n'aurait
    # pas dû atterrir sur un toit). On préfère choisir le 2ᵉ axe minimal.

    if plus_faible == penetration_dessus and vy >= 0:
        # Atterrissage sur le DESSUS de l'obstacle.
        entite.rect.bottom = rect_obstacle.top
        entite.vy          = 0
        entite.on_ground   = True

    elif plus_faible == penetration_dessous and vy <= 0:
        # On a tapé le PLAFOND.
        entite.rect.top = rect_obstacle.bottom
        entite.vy       = 0

    elif plus_faible == penetration_gauche and (not mode_mur or vx >= 0):
        # Bloqué par le bord GAUCHE de l'obstacle (entité va vers la droite).
        entite.rect.right = rect_obstacle.left
        entite.vx         = 0

    elif plus_faible == penetration_droite and (not mode_mur or vx <= 0):
        # Bloqué par le bord DROIT de l'obstacle (entité va vers la gauche).
        entite.rect.left = rect_obstacle.right
        entite.vx        = 0

    elif mode_mur:
        # Cas particulier "coin" ou directions inhabituelles : on force la
        # poussée latérale (sans test vx). Mieux vaut un repoussement
        # imparfait que rester coincé À L'INTÉRIEUR du mur.
        if plus_faible == penetration_gauche:
            entite.rect.right = rect_obstacle.left
            entite.vx         = 0
        elif plus_faible == penetration_droite:
            entite.rect.left = rect_obstacle.right
            entite.vx        = 0


# ═════════════════════════════════════════════════════════════════════════════
#  2. APPLICATION GLOBALE (joueur ↔ toutes les plateformes proches)
# ═════════════════════════════════════════════════════════════════════════════

def appliquer_plateformes(joueur, grille_ou_liste):
    """Résout les collisions du joueur avec toutes les plateformes pertinentes.

    `grille_ou_liste` peut être :
      - une SpatialGrid (méthode .query(rect)) → renvoie SEULEMENT les
        plateformes proches → bien plus rapide sur grandes maps.
      - une liste directe → on les essaye toutes.

    Le test `hasattr(..., 'query')` est du DUCK TYPING : on regarde si
    l'objet sait répondre à `.query()`, et on s'adapte.
    """
    if hasattr(grille_ou_liste, 'query'):
        proches = grille_ou_liste.query(joueur.rect)
    else:
        proches = grille_ou_liste

    for plateforme in proches:
        # Chaque plateforme sait comment se faire-percuter (méthode polymorphe).
        # Permet d'avoir des plateformes "spéciales" (one-way, glissantes...)
        # sans que cette fonction le sache.
        plateforme.verifier_collision(joueur)


# Note : la logique de COMBAT (attaques du joueur, contacts corps-à-corps)
# n'est PAS ici — elle vit dans systems/combat.py.
# Voir resoudre_attaques_joueur() et resoudre_contacts_ennemis() là-bas.
