# Architecture du jeu — LIMINAL (ENTRE-DEUX)

> **À quoi sert ce fichier ?**
> Comprendre **comment le jeu est construit** : qui appelle qui, dans quel
> ordre, et pourquoi. Si tu arrives sur le projet sans l'avoir écrit, lis
> ce fichier en premier.
>
> **Lecture en 10 minutes.**

---

## 1. Le point de départ : `main.py`

Le fichier `main.py` est **minimal** : il crée un objet `Game` et appelle
`game.run()`. Tout le reste se passe dans `core/game.py`.

```
main.py ──> core/game.py  Game  ──> boucle principale
```

---

## 2. La boucle de jeu (`core/game.py`)

C'est le **cœur** du programme. Voici, en pseudo-code, ce qui se passe
**80 fois par seconde** (on vise 80 FPS) :

```
run():
    while True:
        dt = temps écoulé depuis la frame précédente

        # 1. Lire les entrées (clavier, souris, manette)
        event_handler.gérer_événements(...)

        # 2. Mettre à jour la logique du jeu
        if état == "jeu":
            joueur.update(dt)
            ennemis.update(dt)
            compagnons.update(dt, joueur)
            peur.update(dt)
            caméra.suivre(joueur)
            ...
        elif état == "menu":
            menu.update(...)
        elif état == "dialogue":
            dialogue.update(...)
        ...

        # 3. Dessiner
        screen.fill(couleur_fond)
        dessiner_monde()
        dessiner_ennemis()
        dessiner_joueur()
        dessiner_compagnons()
        dessiner_HUD()
        pygame.display.flip()
```

**Points clés :**
- L'ordre des **updates** est important (ex. : le joueur avant la caméra).
- L'ordre des **draws** fait les **calques** : ce qui est dessiné en
  dernier est au-dessus.
- Un **état** (`self.etat = "jeu" / "menu" / "dialogue" / "mort"`) décide
  quoi exécuter.

---

## 3. Qui dépend de qui ?

Vue simplifiée (← signifie « importe ») :

```
main.py
  └── core/game.py
        ├── settings.py                     (constantes)
        ├── core/event_handler.py           (entrées clavier/manette)
        ├── core/save_manager.py            (save.json)
        ├── entities/player.py
        ├── entities/enemy.py
        ├── entities/compagnon.py  ←  systems/compagnons.py
        ├── entities/pnj.py
        ├── world/tilemap.py
        ├── world/collision.py
        ├── world/editor.py                 (mode édition seulement)
        ├── systems/fear_system.py
        ├── systems/combat.py
        ├── systems/lighting.py
        ├── systems/particles.py
        ├── systems/juice.py
        ├── systems/health_overlay.py
        ├── ui/menu.py
        ├── ui/hud.py
        ├── ui/dialogue_box.py
        └── ui/settings_screen.py
```

**Règle :** `settings.py` est importé par tout le monde, mais lui n'importe
personne. C'est la **feuille** de l'arbre.

---

## 4. Les grandes familles

### 4.1 `core/` — la boucle et les entrées

- `game.py` : la classe `Game` (boucle principale, état du jeu).
- `event_handler.py` : lit les touches / boutons manette / souris et
  traduit en actions (saut, attaque, pause...).
- `save_manager.py` : lecture/écriture de `save.json`.

### 4.2 `entities/` — les êtres vivants

Chaque fichier = une **classe** d'entité qui a :
- une position (`self.x`, `self.y`)
- une vitesse (`self.vx`, `self.vy`)
- une hitbox (`self.rect`)
- un état (`self.etat`)
- une méthode `update(dt, ...)`
- une méthode `draw(surf, camera)`

Fichiers :
- `player.py` (joueur)
- `enemy.py` (ennemis)
- `compagnon.py` (blobs blancs qui suivent)
- `pnj.py` (personnages non-joueurs qui parlent)

### 4.3 `systems/` — mécaniques globales

Pas de « corps » visible, mais un effet sur tout le jeu :
- `fear_system.py` : jauge de peur (0-100)
- `combat.py` : règle les dégâts entre joueur et ennemis
- `lighting.py` : voile sombre + halos lumineux
- `particles.py` : petites particules (poussière, étincelles...)
- `juice.py` : **game juice** = screen shake, hit-stop, etc.
- `health_overlay.py` : cœurs animés au-dessus du joueur quand il prend
  un coup (style Hollow Knight).
- `compagnons.py` : **groupe** de compagnons (la classe `Compagnon`
  elle-même est dans `entities/`).

### 4.4 `world/` — la carte

- `tilemap.py` : charge et affiche la carte (plateformes, décor).
- `collision.py` : règles de collision avec les plateformes.
- `editor.py` : éditeur de niveaux intégré (touches 1-6 pour les modes).

### 4.5 `ui/` — tout ce qui est affiché « par-dessus »

- `menu.py` : menu principal + menu pause.
- `hud.py` : cœurs + jauge de peur + FPS.
- `dialogue_box.py` : boîte de dialogue (quand on parle à un PNJ).
- `settings_screen.py` : menu Paramètres.

---

## 5. Flux typique : « le joueur saute »

1. Joueur appuie sur **Espace**.
2. `event_handler.py` reçoit `KEYDOWN` / `K_SPACE`.
3. `event_handler` appelle `joueur.sauter()`.
4. `joueur.sauter()` vérifie les conditions (au sol ? coyote time ?
    double-saut dispo ?) puis met `self.vy = -JUMP_POWER`.
5. À la frame suivante, `joueur.update(dt)` applique la gravité et
    avance : `self.y += self.vy * dt`.
6. `collision.resoudre_collisions(...)` arrête le joueur contre les
    plateformes.
7. `camera.suivre(joueur)` recale la caméra.
8. `joueur.draw(...)` dessine le sprite.

---

## 6. Flux typique : « le joueur prend un coup »

1. `systems/combat.py` détecte `joueur.rect.colliderect(ennemi.rect)`.
2. Si le joueur n'est **pas** invincible :
   - `joueur.pv -= 1`
   - `joueur.invincible_temps = INVINCIBLE_DURATION`
   - `joueur.vx = ±KNOCKBACK_PLAYER` (recul)
   - `juice.add_shake(...)` (secouer l'écran)
   - `juice.add_hitstop(...)` (micro-pause)
   - `peur.increase(...)`
3. Le HUD s'affiche (cœurs + barre de peur) pendant `HP_DISPLAY_DURATION`.
4. Si `joueur.pv <= 0`, `game.etat = "mort"`.

---

## 7. Pourquoi cette architecture ?

- **Séparation des responsabilités** : le joueur ne sait pas dessiner la
  carte, la carte ne sait pas que le joueur existe. Chacun son métier.
- **Testabilité** : on peut changer les ennemis sans toucher à la carte.
- **Lisibilité** : quand on cherche « où est géré le dash ? », on va
  direct dans `entities/player.py`, pas besoin de tout relire.
- **Collaboration** : plusieurs personnes peuvent bosser sur des fichiers
  différents sans conflit Git.

Pour **savoir où modifier quoi**, voir `docs/OU_EST_QUOI.md`.
