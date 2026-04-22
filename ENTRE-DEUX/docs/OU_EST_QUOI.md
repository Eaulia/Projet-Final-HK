# Où est quoi ? — Index rapide LIMINAL

> **À quoi sert ce fichier ?**
> Tu veux modifier quelque chose, tu sais **quoi**, mais tu ne sais pas
> **où**. Cherche ici : chaque entrée te dit le fichier, la fonction et
> la ligne (approximative) à modifier.
>
> **Astuce** : utilise `Ctrl+F` dans ton éditeur pour chercher un mot-clé
> en français dans cette page.

---

## 🎮 Gameplay — Joueur

| Je veux modifier…                          | Fichier                    | Où exactement                       |
|--------------------------------------------|----------------------------|-------------------------------------|
| Vitesse de course                          | `settings.py`              | `PLAYER_SPEED`                      |
| Hauteur de saut                            | `settings.py`              | `JUMP_POWER`                        |
| Force de gravité                           | `settings.py`              | `GRAVITY`                           |
| PV max                                     | `settings.py`              | `PLAYER_MAX_HP`                     |
| Durée d'invincibilité après un coup        | `settings.py`              | `INVINCIBLE_DURATION`               |
| Comportement du joueur chaque frame        | `entities/player.py`       | méthode `update()`                  |
| Animation (cycle des sprites)              | `entities/player.py`       | méthode `_avancer_anim()`           |
| Touches associées aux actions              | `core/event_handler.py`    | fonction `_gerer_touches_jeu()`     |
| Mapping manette PS5                        | `settings.py`              | section 9 (`BTN_CROIX`, etc.)       |

## 🎯 Capacités (Hollow Knight)

| Je veux modifier…                          | Fichier                    | Où exactement                       |
|--------------------------------------------|----------------------------|-------------------------------------|
| Vitesse / durée du dash                    | `settings.py`              | `DASH_SPEED`, `DASH_DURATION`       |
| Cooldown du dash                           | `settings.py`              | `DASH_COOLDOWN`                     |
| Double-saut (activer / désactiver)         | `entities/player.py`       | méthode `sauter()`                  |
| Force du double-saut                       | `settings.py`              | `DOUBLE_JUMP_POWER`                 |
| Wall-slide (vitesse de chute sur mur)      | `settings.py`              | `WALL_SLIDE_SPEED`                  |
| Wall-jump (impulsion)                      | `settings.py`              | `WALL_JUMP_VX`, `WALL_JUMP_VY`      |
| Coyote time / jump buffer                  | `settings.py`              | `COYOTE_TIME`, `JUMP_BUFFER`        |

## ⚔️ Combat

| Je veux modifier…                          | Fichier                    | Où exactement                       |
|--------------------------------------------|----------------------------|-------------------------------------|
| Dégâts du joueur aux ennemis               | `systems/combat.py`        | fonction `degats_aux_ennemis()`     |
| Dégâts des ennemis au joueur               | `systems/combat.py`        | fonction `degats_au_joueur()`       |
| Force du knockback                         | `settings.py`              | `KNOCKBACK_PLAYER/ENEMY`            |
| Durée d'une attaque                        | `settings.py`              | `ATTACK_DURATION`                   |
| Taille de la hitbox d'attaque              | `settings.py`              | `ATTACK_RECT_W/H`                   |
| Pogo (rebond sur ennemi par le bas)        | `entities/player.py`       | méthode `attaquer_bas()`            |
| Régénération passive (délai, intervalle)   | `settings.py`              | `REGEN_DELAY`, `REGEN_INTERVAL`     |

## 👻 Ennemis

| Je veux modifier…                          | Fichier                    | Où exactement                       |
|--------------------------------------------|----------------------------|-------------------------------------|
| Vitesse / PV / dégâts d'un ennemi          | `entities/enemy.py`        | `__init__` de chaque type           |
| Ajouter un nouveau type d'ennemi           | `entities/enemy.py`        | nouvelle classe                     |
| IA des ennemis                             | `entities/enemy.py`        | méthode `update()` de chaque classe |
| Apparition (spawn) des ennemis             | `world/tilemap.py`         | fonction `charger_ennemis()`        |

## 🌫️ Peur & compagnons

| Je veux modifier…                          | Fichier                    | Où exactement                       |
|--------------------------------------------|----------------------------|-------------------------------------|
| Vitesse de montée de la peur               | `systems/fear_system.py`   | `FEAR_RATE_UP`                      |
| Voile sombre (quand peur élevée)           | `systems/fear_system.py`   | méthode `draw()`                    |
| Apparence des compagnons (blobs blancs)    | `entities/compagnon.py`    | méthodes `_dessiner_*()`            |
| Vitesse des compagnons                     | `settings.py`              | `COMPAGNON_VITESSE_MARCHE/COURSE`   |
| Distance rassurante / trop loin            | `settings.py`              | `COMPAGNON_DIST_*`                  |
| Effet des compagnons sur la peur           | `systems/compagnons.py`    | méthode `affecter_peur()`           |
| Animation cape (touche C)                  | `entities/compagnon.py`    | `DUREE_ANIM_CAPE` + `draw()`        |
| Nombre de compagnons au démarrage          | `game_config.json`         | clé `"nb_compagnons"`               |

## 🎨 Affichage / HUD

| Je veux modifier…                          | Fichier                    | Où exactement                       |
|--------------------------------------------|----------------------------|-------------------------------------|
| Résolution de la fenêtre                   | `settings.py`              | `WIDTH`, `HEIGHT`                   |
| FPS cible                                  | `settings.py`              | `FPS`                               |
| Couleurs globales                          | `settings.py`              | section 2                           |
| Cœurs dans le HUD                          | `ui/hud.py`                | méthode `_dessiner_coeurs()`        |
| Mode HUD (permanent / immersion)           | `settings.py`              | `hud_mode` (runtime)                |
| Cœurs au-dessus du joueur                  | `systems/health_overlay.py`| méthode `draw()`                    |
| Jauge de peur                              | `ui/hud.py`                | méthode `_dessiner_jauge_peur()`    |
| Caméra (lissage, offset)                   | `settings.py`              | `CAMERA_FOLLOW_SPEED`, `CAMERA_Y_OFFSET` |

## 💡 Ambiance

| Je veux modifier…                          | Fichier                    | Où exactement                       |
|--------------------------------------------|----------------------------|-------------------------------------|
| Obscurité ambiante                         | `settings.py`              | `FOND_ALPHA`                        |
| Rayon du halo autour du joueur             | `settings.py`              | `RAYON_JOUEUR`                      |
| Particules (densité, couleur)              | `systems/particles.py`     | paramètres dans `__init__`          |
| Screen shake (intensité, durée)            | `systems/juice.py`         | méthode `add_shake()`               |

## 🗺️ Carte & éditeur

| Je veux modifier…                          | Fichier                    | Où exactement                       |
|--------------------------------------------|----------------------------|-------------------------------------|
| Ajouter une plateforme en jeu              | — (éditeur)                | touche `E` puis clic                |
| Charger une carte différente               | `core/game.py`             | méthode `_charger_carte()`          |
| Format de la carte (JSON)                  | `map.json`                 | fichier lui-même                    |
| Modes de l'éditeur (1-6)                   | `world/editor.py`          | constantes en haut du fichier       |
| Mode 6 (hitbox des sprites)                | `world/editor.py`          | méthode `_afficher_mode6()`         |

## 🎵 Audio

| Je veux modifier…                          | Fichier                    | Où exactement                       |
|--------------------------------------------|----------------------------|-------------------------------------|
| Volume musique                             | `settings.py`              | `VOLUME_MUSIQUE`                    |
| Durée de fondu entrant                     | `settings.py`              | `FADEIN_MUSIQUE_MS`                 |
| Musique d'une scène                        | `core/game.py`             | méthode `_charger_audio_ambiance()` |

## 📋 Menus

| Je veux modifier…                          | Fichier                    | Où exactement                       |
|--------------------------------------------|----------------------------|-------------------------------------|
| Menu principal (texte, ordre)              | `ui/menu.py`               | méthode `_dessiner_menu_principal()`|
| Menu pause                                 | `ui/menu.py`               | méthode `_dessiner_menu_pause()`    |
| Menu Paramètres                            | `ui/settings_screen.py`    | méthode `draw()`                    |
| Boîte de dialogue (PNJ)                    | `ui/dialogue_box.py`       | classe `DialogueBox`                |

## 💾 Sauvegarde

| Je veux modifier…                          | Fichier                    | Où exactement                       |
|--------------------------------------------|----------------------------|-------------------------------------|
| Ce qui est sauvegardé                      | `core/save_manager.py`     | fonctions `save()` / `load()`       |
| Fichier de configuration (nb_compagnons…)  | `game_config.json`         | fichier lui-même                    |

---

## 🔎 Je ne trouve pas ce que je cherche

1. Ouvre `ARCHITECTURE.md` pour retrouver la **famille** concernée.
2. Utilise **Ctrl+F dans ton IDE** sur le mot-clé (ex. `dash`, `peur`,
    `compagnon`).
3. Regarde dans `DICTIONNAIRE.md` si c'est un **concept** technique
    (lerp, delta-time, SRCALPHA…).
