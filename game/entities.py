import random
from pygame import Rect

# Entidades: Heroi, Inimigo, Moeda
class Hero:
    def __init__(self, x, y, actor_factory):
        # actor_factory é uma função que cria Actor no runtime do pgzero
        self.actor = actor_factory("hero_idle1", (x, y))
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.prev_y = y
        self.frame = 0
        self.anim_speed = 0.15
        self.idle_frames = ["hero_idle1"]
        self.run_frames = ["hero_run1", "hero_run2", "hero_run3", "hero_run4"]

    def update(self, keyboard, gravity, ground_y, sound_enabled, sounds):
        self.vx = 0
        if keyboard.left:
            self.vx = -3
        if keyboard.right:
            self.vx = 3
        if keyboard.space and self.on_ground:
            # pulo um pouco mais forte para facilitar stomp
            self.vy = -14
            self.on_ground = False
            try:
                if sound_enabled:
                    sounds.jump.play()
            except Exception:
                pass

        try:
            self.prev_y = self.actor.y
        except Exception:
            pass

        self.vy += gravity
        self.actor.x += self.vx
        self.actor.y += self.vy

        # calcular altura do sprite de forma robusta: preferir actor.height, depois images[...] se disponível
        img_h = None
        try:
            img_h = getattr(self.actor, 'height', None)
        except Exception:
            img_h = None
        if not img_h:
            try:
                img_name = getattr(self.actor, 'image', None)
                img_h = images.__getattr__(img_name).get_height()
            except Exception:
                img_h = 32

        bottom = self.actor.y + img_h / 2

        if bottom >= ground_y():
            try:
                self.actor.y = ground_y() - img_h / 2
            except Exception:
                # garantia simples caso images/height não estejam disponíveis
                try:
                    self.actor.y = ground_y() - getattr(self.actor, 'height', img_h) / 2
                except Exception:
                    self.actor.y = ground_y()
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        frames = self.run_frames if self.vx != 0 else self.idle_frames
        self.frame = (self.frame + self.anim_speed) % max(1, len(frames))
        try:
            self.actor.image = frames[int(self.frame) % len(frames)]
        except Exception:
            pass
        if self.vx < 0:
            self.actor.flip_x = True
        elif self.vx > 0:
            self.actor.flip_x = False


class Enemy:
    def __init__(self, x, y, patrol_range=100, actor_factory=None):
        self.actor = actor_factory("enemy1", (x, y)) if actor_factory else None
        self.start_x = x
        self.range = patrol_range
        self.speed = 1.5
        self.dir = 1
        self.hp = 1
        self.frame = 0
        self.dead = False

    def update(self):
        try:
            self.actor.x += self.speed * self.dir
            if abs(self.actor.x - self.start_x) > self.range:
                self.dir *= -1
            self.frame = (self.frame + 0.12) % 3
            try:
                self.actor.image = ["enemy1", "enemy2", "enemy3"][int(self.frame)]
            except Exception:
                pass
        except Exception:
            pass

    def take_damage(self, coins_list, coin_factory):
        self.hp -= 1
        if self.hp <= 0:
            # dropa moeda
            coins_list.append(coin_factory(self.actor.x, self.actor.y))
            # marcar como morto — o orquestrador deve remover esta entidade
            self.dead = True


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frames = ["coin_gold", "coin_gold_side"]
        self.frame = 0

    def update(self):
        self.frame = (self.frame + 0.2) % len(self.frames)

    def rect(self, images):
        try:
            img = images.__getattr__(self.frames[0])
            return Rect(self.x - img.get_width() / 2, self.y - img.get_height() / 2, img.get_width(), img.get_height())
        except Exception:
            return Rect(self.x, self.y, 16, 16)
