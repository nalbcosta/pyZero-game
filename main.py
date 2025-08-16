# Imports iniciais
import pgzrun
from pygame import Rect
import random
import math

# Constantes do Jogo
WIDTH = 640
HEIGHT = 480
TITLE = "RogueQuest"

# Estados do Jogo
MENU, GAME, SETTINGS = 'menu', 'game', 'settings'
game_state = MENU

# Som/música flags
music_on = True
sound_on = True

# Botões do menu (Rect: x, y, w, h)
menu_buttons = {
    "start": Rect(220, 150, 200, 50),
    "settings": Rect(220, 220, 200, 50),
    "quit": Rect(220, 290, 200, 50)
}

settings_buttons = {
    "music": Rect(220, 150, 200, 50),
    "sound": Rect(220, 220, 200, 50),
    "back": Rect(220, 290, 200, 50)
}

# Sprites dos Inimigos e do Herói
class SpriteAnimator:
    def __init__(self, images, speed=0.15):
        self.images = images
        self.index = 0
        self.speed = speed

    def update(self):
        self.index = (self.index + self.speed) % len(self.images)

    def get_image(self):
        return self.images[int(self.index)]
    
class Hero:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 32, 32)
        self.anim_idle = SpriteAnimator([f"hero_idle_{i}.png" for i in range(4)])
        self.anim_move = SpriteAnimator([f"hero_move_{i}.png" for i in range(4)])
        self.moving = False
        self.target = (x, y)
        
    def update(self):
        if self.rect.topleft != self.target:
            self.moving = True
            dx = self.target[0] - self.rect.x
            dy = self.target[1] - self.rect.y
            dist = math.hypot(dx, dy)
            if dist > 1:
                self.rect.x += int(dx / dist)
                self.rect.y += int(dy / dist)
            else:
                self.rect.topleft = self.target
                self.moving = False
        if self.moving:
            self.anim_move.update()
        else:
            self.anim_idle.update()

    def draw(self):
        img = self.anim_move.get_image() if self.moving else self.anim_idle.get_image()
        screen.blit(img, self.rect.topleft)


class Enemy:
    def __init__(self, x, y, territory):
        self.rect = Rect(x, y, 32, 32)
        self.territory = territory
        self.anim_idle = SpriteAnimator([f"enemy_idle_{i}.png" for i in range(4)])
        self.anim_move = SpriteAnimator([f"enemy_move_{i}.png" for i in range(4)])
        self.target = self.random_point()
        self.moving = False
        

    def random_point(self):
        return (
            random.randint(self.territory.left, self.territory.right - 32),
            random.randint(self.territory.top, self.territory.bottom - 32)
        )

    def update(self):
        if self.rect.topleft != self.target:
            self.moving = True
            dx = self.target[0] - self.rect.x
            dy = self.target[1] - self.rect.y
            dist = math.hypot(dx, dy)
            if dist > 1:
                self.rect.x += int(dx / dist)
                self.rect.y += int(dy / dist)
            else:
                self.rect.topleft = self.target
                self.moving = False
        else:
            self.target = self.random_point()
        if self.moving:
            self.anim_move.update()
        else:
            self.anim_idle.update()
    
    def draw(self):
        img = self.anim_move.get_image() if self.moving else self.anim_idle.get_image()
        screen.blit(img, self.rect.topleft)
        
# Objetos do Jogo
hero = Hero(64, 64)
enemies = [
    Enemy(100, 100, Rect(50, 50, 200, 200)),
    Enemy(300, 150, Rect(250, 100, 100, 200)),
    Enemy(400, 300, Rect(350, 250, 200, 100))
]


def draw():
    screen.clear()
    if game_state == MENU:
        draw_menu()
    elif game_state == GAME:
        draw_game()
    elif game_state == SETTINGS:
        draw_settings()

def draw_menu():
    screen.draw.text("ROGUELIKE", center=(WIDTH//2, 80), fontsize=60, color="white")
    for name, rect in menu_buttons.items():
        screen.draw.filled_rect(rect, "darkblue")
        screen.draw.text(name.capitalize(), center=rect.center, fontsize=36, color="white")

def draw_settings():
    screen.draw.text("SETTINGS", center=(WIDTH//2, 80), fontsize=60, color="white")
    screen.draw.filled_rect(settings_buttons["music"], "darkblue")
    screen.draw.text(f"Music: {'On' if music_on else 'Off'}", center=settings_buttons["music"].center, fontsize=36, color="white")
    screen.draw.filled_rect(settings_buttons["sound"], "darkblue")
    screen.draw.text(f"Sound: {'On' if sound_on else 'Off'}", center=settings_buttons["sound"].center, fontsize=36, color="white")
    screen.draw.filled_rect(settings_buttons["back"], "darkblue")
    screen.draw.text("Back", center=settings_buttons["back"].center, fontsize=36, color="white")

def draw_game():
    # Draw map grid (roguelike style)
    for y in range(0, HEIGHT, 32):
        for x in range(0, WIDTH, 32):
            screen.draw.rect(Rect(x, y, 32, 32), "gray")
    hero.draw()
    for enemy in enemies:
        enemy.draw()

def update():
    if game_state == GAME:
        hero.update()
        for enemy in enemies:
            enemy.update()

def on_mouse_down(pos):
    global game_state, music_on, sound_on
    if game_state == MENU:
        for name, rect in menu_buttons.items():
            if rect.collidepoint(pos):
                if name == "start":
                    game_state = GAME
                elif name == "settings":
                    game_state = SETTINGS
                elif name == "quit":
                    exit()
    elif game_state == SETTINGS:
        if settings_buttons["music"].collidepoint(pos):
            music_on = not music_on
        elif settings_buttons["sound"].collidepoint(pos):
            sound_on = not sound_on
        elif settings_buttons["back"].collidepoint(pos):
            game_state = MENU
    elif game_state == GAME:
        # Move hero to clicked cell (centered)
        cell_x = (pos[0] // 32) * 32
        cell_y = (pos[1] // 32) * 32
        hero.target = (cell_x, cell_y)

pgzrun.go()