# Dictionnaire du code — LIMINAL (ENTRE-DEUX)

> **À quoi sert ce fichier ?**
> Quand tu lis le code et que tu tombes sur un mot ou une fonction que tu ne
> connais pas, cherche-le ici. Chaque entrée a un numéro (ex. `[D3]`) qui est
> référencé dans les commentaires du code.
>
> Les entrées sont classées par **thème** (pas par ordre alphabétique) pour
> que tu puisses lire d'un bout à l'autre comme un cours.
>
> Niveau visé : **première NSI**. Si un concept demande plus, il est détaillé
> ici avec un mini-exemple.

---

## Sommaire

- **Pygame de base**
  - [D1] `pygame.Surface` — la « feuille de dessin »
  - [D2] `SRCALPHA` — dessiner avec de la transparence
  - [D3] `blit` — coller une image sur une autre
  - [D4] `pygame.Rect` — un rectangle (position + taille)
  - [D5] `colliderect` — tester si deux rectangles se chevauchent
  - [D6] `pygame.draw.rect` / `pygame.draw.ellipse` — dessiner des formes
  - [D7] `pygame.event` — clavier, souris, manette
- **Maths du jeu**
  - [D10] `dt` (delta time) — le temps qui s'écoule entre deux frames
  - [D11] `math.hypot(dx, dy)` — distance entre deux points
  - [D12] `math.sin(t)` — une oscillation (flottement, respiration)
  - [D13] Interpolation linéaire (`lerp`) — fondu progressif entre deux valeurs
  - [D14] Normaliser un vecteur — obtenir une direction de longueur 1
- **Concepts du jeu**
  - [D20] Caméra (`camera.offset_x`, `camera.offset_y`)
  - [D21] Hitbox vs sprite
  - [D22] Machine à états (state machine)
  - [D23] `coyote time` et `jump buffer`
- **Python utile**
  - [D30] `self` — le fameux argument de méthode
  - [D31] `__init__` — le constructeur
  - [D32] f-strings (`f"bonjour {nom}"`)
  - [D33] Liste en compréhension (`[x*2 for x in liste]`)
  - [D34] Lambda (`lambda x: x+1`)
  - [D35] Dictionnaire JSON (sauvegardes)
- **Organisation du projet**
  - [D40] Pourquoi autant de dossiers ? (core, entities, systems, ui, world)

---

# Pygame de base

## [D1] `pygame.Surface` — la « feuille de dessin »

Une `Surface` est **une image en mémoire** sur laquelle on peut dessiner.
L'écran du jeu est lui-même une `Surface` (la plus grande).

```python
import pygame
surf = pygame.Surface((100, 50))     # image noire de 100×50 pixels
surf.fill((255, 0, 0))               # on la remplit en rouge
```

**Dans le jeu :**
- `self.screen` dans `core/game.py` → la grande surface = l'écran
- Chaque sprite chargé est une Surface
- Certains effets (halos, overlays) sont dessinés sur des surfaces
  temporaires qu'on colle ensuite à l'écran

## [D2] `SRCALPHA` — dessiner avec de la transparence

Par défaut, une `Surface` est **opaque** : si on la colle sur l'écran,
les pixels noirs écrasent le fond. Pour avoir de la transparence, on passe
le drapeau `pygame.SRCALPHA` :

```python
halo = pygame.Surface((200, 200), pygame.SRCALPHA)
# Maintenant halo a 4 canaux : R, G, B et Alpha (transparence).
# Les pixels non dessinés restent totalement transparents (alpha = 0).
```

**Dans le jeu :** on s'en sert pour tout ce qui est « par-dessus le monde »
avec du flou : halos de lumière, dégâts rouges, voile de peur.

## [D3] `blit` — coller une image sur une autre

`blit` vient de « block transfer ». Ça veut dire : **prendre un bloc de
pixels et le coller quelque part**.

```python
ecran.blit(sprite_joueur, (x, y))   # colle le sprite en position (x, y)
```

La position `(x, y)` est **le coin supérieur gauche** du sprite, pas son
centre. C'est un piège classique.

## [D4] `pygame.Rect` — un rectangle (position + taille)

Un `Rect` stocke 4 entiers : `x, y, width, height`.

```python
r = pygame.Rect(100, 200, 50, 80)
r.x, r.y       # coin haut-gauche
r.centerx      # x du centre
r.bottom       # y du bas (= y + height)
```

**Dans le jeu :** les hitboxes du joueur et des ennemis sont des `Rect`.

## [D5] `colliderect` — tester si deux rectangles se chevauchent

```python
if hitbox_joueur.colliderect(hitbox_ennemi):
    # le joueur touche l'ennemi → dégâts
```

Renvoie `True` dès qu'il y a **un pixel** de recouvrement.

## [D6] `pygame.draw.rect` / `pygame.draw.ellipse` — dessiner des formes

```python
pygame.draw.rect(surf, couleur, rect)           # rectangle plein
pygame.draw.rect(surf, couleur, rect, 2)        # contour de 2 px
pygame.draw.ellipse(surf, couleur, rect)        # ellipse dans le rect
pygame.draw.line(surf, couleur, (x1,y1), (x2,y2), 3)
```

**Dans le jeu :** les compagnons (blobs blancs) sont dessinés avec
`ellipse`. Les barres de vie / jauges sont des `rect`.

## [D7] `pygame.event` — clavier, souris, manette

Chaque frame, pygame remplit une file d'événements qu'on lit une fois :

```python
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        ...
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            ...
```

**Dans le jeu :** tout ça est centralisé dans `core/event_handler.py`.

---

# Maths du jeu

## [D10] `dt` (delta time) — le temps qui s'écoule entre deux frames

Si on écrit `x += 5` chaque frame, la vitesse dépend du FPS : sur un PC
rapide on va 2× plus vite que sur un PC lent. Pour éviter ça, on multiplie
par `dt` (le temps depuis la dernière frame, en secondes) :

```python
x += vitesse * dt    # vitesse est en pixels PAR SECONDE
```

Avec `FPS = 80`, `dt ≈ 1/80 ≈ 0.0125 s`.

**Règle :** toute valeur en px/s, m/s² ou « par seconde » doit être
multipliée par `dt` dans les calculs.

## [D11] `math.hypot(dx, dy)` — distance entre deux points

`math.hypot` calcule `sqrt(dx² + dy²)` — c'est le théorème de Pythagore.

```python
import math
dx = cible.x - joueur.x
dy = cible.y - joueur.y
distance = math.hypot(dx, dy)    # distance en pixels
```

Plus propre que `math.sqrt(dx*dx + dy*dy)`.

## [D12] `math.sin(t)` — une oscillation (flottement, respiration)

`math.sin` oscille entre -1 et +1. Si on lui donne un temps qui avance, on
obtient un mouvement de va-et-vient régulier :

```python
# Flottement vertical : amplitude 4 px, période ≈ 2π / 3 ≈ 2.1 s
y_affichage = y + 4 * math.sin(3 * t)
```

**Dans le jeu :** flottement des compagnons, respiration des halos.

## [D13] Interpolation linéaire (`lerp`) — fondu progressif

On veut qu'une valeur **A** glisse doucement vers une valeur **B**. La
formule clé :

```python
valeur = (1 - t) * A + t * B
```

- `t = 0` → on obtient A
- `t = 1` → on obtient B
- `t = 0.5` → pile au milieu

**Dans le jeu :**
- La caméra suit le joueur : `camera_x = lerp(camera_x, joueur_x, 0.1)`
- Les compagnons rentrent dans le joueur en rétrécissant (animation de cape)

## [D14] Normaliser un vecteur — obtenir une direction de longueur 1

Un « vecteur vitesse » peut avoir n'importe quelle longueur. Pour avancer à
une vitesse fixe V vers une cible, on divise le vecteur direction par sa
longueur, puis on multiplie par V :

```python
dx = cible.x - moi.x
dy = cible.y - moi.y
d  = math.hypot(dx, dy)      # longueur du vecteur
if d > 0:
    vx = (dx / d) * V        # composante x à vitesse V
    vy = (dy / d) * V
```

C'est ce que font les compagnons pour avancer vers le joueur.

---

# Concepts du jeu

## [D20] Caméra (`camera.offset_x`, `camera.offset_y`)

Le « monde » est plus grand que l'écran. La caméra stocke un décalage :

```python
# Pour dessiner un objet du monde à l'écran :
x_ecran = x_monde - camera.offset_x
y_ecran = y_monde - camera.offset_y
```

Quand la caméra suit le joueur, `offset_x` augmente → tout le monde se
décale à gauche → le joueur reste au centre.

## [D21] Hitbox vs sprite

Le **sprite** est l'image affichée. La **hitbox** est un rectangle
invisible utilisé pour les collisions. Les deux ont souvent des tailles
différentes : on veut une hitbox plus petite que le sprite pour que le jeu
soit **juste** (pas de dégâts quand on pense avoir évité).

## [D22] Machine à états (state machine)

Un personnage est toujours dans **un seul** état à la fois. On stocke son
état dans une chaîne, et on change d'état selon les conditions :

```python
if self.etat == "suit":
    # comportement 1
elif self.etat == "court":
    # comportement 2
```

**Dans le jeu :** joueur, ennemis, compagnons, PNJ utilisent tous des
machines à états.

## [D23] `coyote time` et `jump buffer`

Deux astuces pour que les sauts soient **agréables** :

- **Coyote time** : après avoir quitté le bord d'une plateforme, on peut
  encore sauter pendant ~0.1 s (comme Wile E. Coyote qui court dans le
  vide avant de tomber).
- **Jump buffer** : si on appuie sur saut ~0.12 s avant d'atterrir, le saut
  se déclenche pile à l'atterrissage.

Les deux valeurs sont dans `settings.py` (`COYOTE_TIME`, `JUMP_BUFFER`).

---

# Python utile

## [D30] `self` — le fameux argument de méthode

`self` est **l'objet en cours** sur lequel la méthode est appelée. En
dehors de la classe, `joueur.bouger()` est traduit en `Player.bouger(joueur)`
— donc `self = joueur`.

Tu accèdes aux variables de l'objet avec `self.nom_variable`.

## [D31] `__init__` — le constructeur

Appelé automatiquement à la création d'un objet :

```python
j = Player(100, 400)     # ← appelle Player.__init__(self, 100, 400)
```

C'est là qu'on initialise toutes les variables avec `self.x = x`, etc.

## [D32] f-strings — chaînes formatées

```python
nom = "Edison"
pv  = 3
print(f"{nom} a {pv} PV")        # → "Edison a 3 PV"
print(f"FPS = {clock.get_fps():.1f}")   # arrondi à 1 décimale
```

Le `f` avant le guillemet autorise les `{expressions}` à l'intérieur.

## [D33] Liste en compréhension

Une syntaxe compacte pour construire une liste :

```python
carres = [x*x for x in range(10)]        # [0, 1, 4, 9, 16, ...]
pairs  = [x for x in liste if x % 2 == 0]
```

Équivalent en version longue :

```python
carres = []
for x in range(10):
    carres.append(x*x)
```

## [D34] Lambda — mini-fonction en une ligne

```python
carre = lambda x: x*x
carre(5)    # 25
```

Utile pour `sorted(liste, key=lambda obj: obj.priorite)` : on trie une
liste d'objets selon un critère calculé à la volée.

## [D35] Dictionnaire JSON (sauvegardes)

Un `dict` Python se traduit directement en JSON :

```python
import json
data = {"pv": 5, "position": [100, 200]}
with open("save.json", "w") as f:
    json.dump(data, f, indent=2)        # écrit le fichier
```

Relecture :

```python
with open("save.json") as f:
    data = json.load(f)
print(data["pv"])
```

**Dans le jeu :** `save.json`, `game_config.json`, `hitboxes.json`,
`map.json` sont tous lus/écrits comme ça.

---

# Organisation du projet

## [D40] Pourquoi autant de dossiers ?

```
ENTRE-DEUX/
├── main.py                 lance le jeu
├── settings.py             toutes les constantes
├── utils.py                petites fonctions partagées
├── core/                   logique de haut niveau : la boucle du jeu
├── entities/               tout ce qui « vit » : joueur, ennemis, compagnons, PNJ
├── systems/                systèmes transversaux : peur, combat, lumière...
├── world/                  la carte, les collisions, l'éditeur
├── ui/                     menus, HUD, boîtes de dialogue
├── assets/                 images, polices (PNG, TTF)
├── audio/                  musique et bruitages (OGG, MP3)
└── docs/                   ce dossier — documentation lisible
```

**Règle mentale :**
- Si c'est un **personnage**, c'est dans `entities/`.
- Si c'est un **affichage** qui concerne l'UI, c'est dans `ui/`.
- Si c'est une **mécanique globale** (peur, éclairage), c'est dans `systems/`.
- Si c'est **lié à la carte**, c'est dans `world/`.

Pour savoir **où modifier quoi**, voir `docs/OU_EST_QUOI.md`.
