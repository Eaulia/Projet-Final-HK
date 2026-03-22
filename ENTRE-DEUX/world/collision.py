# ─────────────────────────────────────────
#  ENTRE-DEUX — Résolution des collisions
# ─────────────────────────────────────────


def resoudre_collision(entite, rect_obstacle, mode_mur=False):
    """
    Pousse l'entité hors du rect_obstacle selon l'axe où elle pénètre le moins.

    mode_mur=False (plateformes) :
        On pousse sur les côtés sans vérifier la direction de déplacement.
        Pratique pour les plateformes simples.

    mode_mur=True (murs) :
        On pousse sur les côtés seulement si l'entité se déplaçait vers eux.
        Ça évite qu'un mur propulse le personnage dans la mauvaise direction
        quand il est déjà appuyé contre lui.
    """
    if not entite.rect.colliderect(rect_obstacle):
        return

    # Calcul de la pénétration sur chaque côté
    penetration_gauche  = entite.rect.right  - rect_obstacle.left
    penetration_droite  = rect_obstacle.right - entite.rect.left
    penetration_dessus  = entite.rect.bottom - rect_obstacle.top
    penetration_dessous = rect_obstacle.bottom - entite.rect.top

    # On résout par l'axe où on est le moins enfoncé
    plus_faible = min(
        penetration_gauche,
        penetration_droite,
        penetration_dessus,
        penetration_dessous,
    )

    vy = getattr(entite, 'vy', 0)
    vx = getattr(entite, 'vx', 0)

    if plus_faible == penetration_dessus and vy >= 0:
        # Atterrissage sur le dessus de l'obstacle
        entite.rect.bottom = rect_obstacle.top
        entite.vy = 0
        entite.on_ground = True

    elif plus_faible == penetration_dessous and vy <= 0:
        # Collision avec le plafond de l'obstacle
        entite.rect.top = rect_obstacle.bottom
        entite.vy = 0

    elif plus_faible == penetration_gauche and (not mode_mur or vx >= 0):
        # Bloqué par le côté gauche de l'obstacle
        entite.rect.right = rect_obstacle.left
        entite.vx = 0

    elif plus_faible == penetration_droite and (not mode_mur or vx <= 0):
        # Bloqué par le côté droit de l'obstacle
        entite.rect.left = rect_obstacle.right
        entite.vx = 0

    elif mode_mur:
        # Cas de coin ou conditions vx non remplies → on pousse quand même
        if plus_faible == penetration_gauche:
            entite.rect.right = rect_obstacle.left
            entite.vx = 0
        elif plus_faible == penetration_droite:
            entite.rect.left = rect_obstacle.right
            entite.vx = 0


# ── Fonctions de vérification appelées chaque frame ──────────────────────────

def verifier_attaques(joueur, ennemis):
    """Tue les ennemis touchés par l'attaque du joueur."""
    if not joueur.attacking:
        return
    for ennemi in ennemis:
        if ennemi.alive and ennemi.rect.colliderect(joueur.attack_rect):
            ennemi.alive = False


def appliquer_plateformes(joueur, grille_ou_liste):
    """
    Résout les collisions du joueur avec les plateformes.
    Accepte une SpatialGrid (plus rapide) ou une liste directe.
    """
    if hasattr(grille_ou_liste, 'query'):
        proches = grille_ou_liste.query(joueur.rect)
    else:
        proches = grille_ou_liste

    for plateforme in proches:
        plateforme.verifier_collision(joueur)


def verifier_contact_ennemi(joueur, ennemis):
    """
    Si un ennemi touche le joueur, les deux prennent un recul.
    On s'arrête au premier contact (un seul ennemi par frame).
    """
    if joueur.invincible or joueur.dead:
        return

    for ennemi in ennemis:
        if not ennemi.alive or ennemi.attack_cooldown > 0:
            continue
        if joueur.rect.colliderect(ennemi.rect):
            if ennemi.hit_player(joueur.rect):
                joueur.hit_by_enemy(ennemi.rect)
            return
