# ─────────────────────────────────────────
#  ENTRE-DEUX — Détection des collisions
# ─────────────────────────────────────────

def check_attack_collisions(player, enemies):
    """Vérifie si l'attaque du joueur touche un ennemi."""
    if player.attacking:
        for enemy in enemies:
            if enemy.alive and enemy.rect.colliderect(player.attack_rect):
                enemy.alive = False

def check_platform_collisions(player, platforms):
    """Vérifie les collisions avec les plateformes."""
    for platform in platforms:
        platform.verifier_collision(player)

def check_wall_collisions(player, walls):
    for wall in walls:
        wall.verifier_collision(player)
