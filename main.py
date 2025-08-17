import pgzrun
import random
from pygame import Rect

from game.entities import Hero, Enemy, Coin
from game import ui

WIDTH = 800
HEIGHT = 480
TITLE = "Mini Plataformer"

BG_IMAGE = "background"
TERRAIN_IMAGE = "terrain"
WORLD_WIDTH = 3000

camera_x = 0
menu_camera_x = 0
music_playing = False
MUSIC_VOLUME = 0.35  # volume padrão da música (0.0 - 1.0)

coin_count = 0
MAX_HEALTH = 3
health = MAX_HEALTH

# popups visuais de cura
heal_popups = []


GRAVITY = 0.6

# frames de invulnerabilidade após levar dano
HURT_COOLDOWN = 60

COIN_GOAL = 10
SPAWN_INTERVAL = 180  # frames

state = "menu"
in_game_menu = False
sound_enabled = True
music_enabled = True
in_game_menu_state = 'paused'

hero = None
enemies = []
coins = []
enemies_killed = 0


def ground_y():
    try:
        return HEIGHT - images.terrain.get_height()
    except Exception:
        return HEIGHT - 40


def actor_factory(name, pos):
    return Actor(name, pos)


def safe_play_sound(names):
    """Tenta tocar a primeira sound key disponível dentro de `names` no objeto `sounds`.
    Usa vários nomes como fallback (hurt, damage, hit, coin, heal, powerup)."""
    try:
        for n in names:
            try:
                # tentativa direta: sounds.<name>.play()
                attr = getattr(sounds, n, None)
                if attr:
                    try:
                        attr.play()
                        return
                    except Exception:
                        pass
                # fallback: sounds.play(name) se disponível
                try:
                    play_fn = getattr(sounds, 'play', None)
                    if play_fn:
                        play_fn(n)
                        return
                except Exception:
                    pass
            except Exception:
                pass
    except Exception:
        pass


def make_menu_buttons():
    w = 220
    h = 56
    cx = WIDTH // 2
    start = Rect(cx - w // 2, 160, w, h)
    options = Rect(cx - w // 2, 230, w, h)
    quitb = Rect(cx - w // 2, 300, w, h)
    return {'start': start, 'options': options, 'quit': quitb}


menu_buttons = make_menu_buttons()
menu_options_buttons = {
    'sound': Rect(200, 180, 300, 40),
    'music': Rect(200, 230, 300, 40),
    'back': Rect(200, 300, 200, 40)
}
pause_buttons = {
    'resume': Rect(WIDTH // 2 - 100, HEIGHT // 2 - 40, 200, 36),
    'options': Rect(WIDTH // 2 - 100, HEIGHT // 2 + 4, 200, 36),
    'main_menu': Rect(WIDTH // 2 - 100, HEIGHT // 2 + 48, 200, 36),
    'quit': Rect(WIDTH // 2 - 100, HEIGHT // 2 + 92, 200, 36)
}

# botões para telas finais (game over / vitória)
end_buttons = {
    'restart': Rect(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 40),
    'menu': Rect(WIDTH // 2 - 100, HEIGHT // 2 + 36, 200, 40)
}


def spawn_enemy(x=None):
    # escolher posição evitando o herói e outros inimigos
    safe_distance = 160
    if x is None:
        # tentar várias vezes para achar uma posição segura
        attempts = 0
        candidate = None
        while attempts < 12:
            cx = random.randint(200, WORLD_WIDTH - 200)
            too_close = False
            try:
                if hero:
                    if abs(cx - getattr(hero.actor, 'x', -9999)) < safe_distance:
                        too_close = True
            except Exception:
                pass
            if not too_close:
                for oe in enemies:
                    try:
                        if abs(cx - getattr(oe.actor, 'x', -9999)) < safe_distance:
                            too_close = True
                            break
                    except Exception:
                        pass
            if not too_close:
                candidate = cx
                break
            attempts += 1
        x = candidate if candidate is not None else random.randint(200, WORLD_WIDTH - 200)
    y = ground_y() - 16
    e = Enemy(x, y, patrol_range=120, actor_factory=actor_factory)
    # ajustar Y do actor do inimigo para ficar em cima do terreno
    try:
        e.actor.y = ground_y() - getattr(e.actor, 'height', 24) / 2
    except Exception:
        pass
    enemies.append(e)


def spawn_coins(n=5):
    for _ in range(n):
        x = random.randint(150, WORLD_WIDTH - 150)
        y = ground_y() - 24
        coins.append(Coin(x, y))


def start_game():
    global hero, enemies, coins, state, coin_count, health, camera_x
    coin_count = 0
    health = MAX_HEALTH
    state = "playing"
    camera_x = 0
    hero = Hero(120, ground_y() - 60, actor_factory)
    # reposicionar o herói precisamente sobre o terreno, zerar velocidade
    try:
        # tentar obter altura do sprite via images (runtime pgzero), senão via atributo height
        try:
            img_name = getattr(hero.actor, 'image', None)
            img_h = images.__getattr__(img_name).get_height()
        except Exception:
            img_h = getattr(hero.actor, 'height', 32)
        # garantir que x esteja dentro do mundo
        hero.actor.x = max(40, min(getattr(hero.actor, 'x', 120), WORLD_WIDTH - 40))
        hero.actor.y = ground_y() - img_h / 2
        hero.vy = 0
        hero.vx = 0
        hero.prev_y = hero.actor.y
        hero.on_ground = True
        # timer de invulnerabilidade (i-frames)
        try:
            hero.hurt_timer = 10
        except Exception:
            pass
    except Exception:
        pass
    enemies.clear()
    coins.clear()
    globals()['enemies_killed'] = 0
    # spawn inicial
    for i in range(3):
        spawn_enemy(400 + i * 300)
    # tocar música de fundo se habilitada
    try:
        global music_playing
        if music_enabled and not music_playing:
            try:
                # ajustar volume quando possível
                try:
                    music.set_volume(MUSIC_VOLUME)
                except Exception:
                    pass
                # tentar tocar a música de fundo
                try:
                    music.play('bg_music')
                    music_playing = True
                except Exception:
                    music_playing = False
            except Exception:
                # falha interna ao tentar tocar música
                music_playing = False
    except Exception:
        pass


spawn_timer = 0


def update():
    global camera_x, spawn_timer, coin_count, health, state, in_game_menu
    global menu_camera_x
    if state != "playing":
        # animar panorama do menu
        try:
            menu_camera_x = (menu_camera_x + 0.5) % (WORLD_WIDTH if WORLD_WIDTH > 0 else 800)
        except Exception:
            menu_camera_x = (globals().get('menu_camera_x', 0) + 0.5) % (WORLD_WIDTH if WORLD_WIDTH > 0 else 800)
        return

    # atualiza herói
    try:
        hero.update(keyboard, GRAVITY, ground_y(), sound_enabled, sounds)
    except Exception:
        pass

    # decrementar timer de invulnerabilidade do herói
    try:
        if getattr(hero, 'hurt_timer', 0) > 0:
            hero.hurt_timer = max(0, hero.hurt_timer - 1)
    except Exception:
        pass

    # defesa: garantir que o herói esteja apoiado no terreno (se o update do herói não o fizer)
    try:
        hh = getattr(hero.actor, 'height', 32)
        bottom = hero.actor.y + hh / 2
        if bottom >= ground_y():
            try:
                hero.actor.y = ground_y() - hh / 2
            except Exception:
                hero.actor.y = ground_y()
            try:
                hero.vy = 0
                hero.on_ground = True
            except Exception:
                pass
    except Exception:
        pass

    # atualizar inimigos
    for e in enemies[:]:
        try:
            e.update()
        except Exception:
            pass

    # atualizar moedas
    for c in coins[:]:
        try:
            c.update()
        except Exception:
            pass

    # construir retângulo do herói
    hero_rect = None
    try:
        hx = hero.actor.x
        hy = hero.actor.y
        hw = getattr(hero.actor, 'width', 24)
        hh = getattr(hero.actor, 'height', 32)
        hero_rect = Rect(hx - hw / 2, hy - hh / 2, hw, hh)
    except Exception:
        hero_rect = None

    # colisões herói x coin
    if hero_rect:
        for c in coins[:]:
            try:
                if hero_rect.colliderect(c.rect(images)):
                    coins.remove(c)
                    coin_count += 1
                    try:
                        if sound_enabled:
                            safe_play_sound(['coin', 'pickup', 'collect'])
                    except Exception:
                        pass
            except Exception:
                pass

    # colisões herói x inimigo (stomp básico)
    if hero_rect:
        for e in enemies[:]:
            try:
                ex = e.actor.x
                ey = e.actor.y
                ew = getattr(e.actor, 'width', 24)
                eh = getattr(e.actor, 'height', 24)
                enemy_rect = Rect(ex - ew / 2, ey - eh / 2, ew, eh)
                if hero_rect.colliderect(enemy_rect):
                    # heurística stomp mais estrita: herói está acima e com velocidade descendente
                    try:
                        hero_vy = getattr(hero, 'vy', 0)
                        hero_y = getattr(hero.actor, 'y', 0)
                        enemy_y = getattr(e.actor, 'y', 0)
                    except Exception:
                        hero_vy = getattr(hero, 'vy', 0)
                        hero_y = 0
                        enemy_y = 0
                    if hero_vy > 1 and hero_y < enemy_y - 6:
                        try:
                            e.take_damage(coins, lambda x, y: Coin(x, y))
                        except Exception:
                            pass
                        # pequeno salto de retorno ao stompar
                        try:
                            hero.vy = -8
                        except Exception:
                            pass
                        # remover inimigo imediatamente para evitar múltiplos hits e drops duplicados
                        try:
                            if e in enemies:
                                enemies.remove(e)
                        except Exception:
                            pass
                        # contabilizar abate e curar a cada 2 inimigos
                        try:
                            globals()['enemies_killed'] = globals().get('enemies_killed', 0) + 1
                            if globals().get('enemies_killed', 0) >= 2:
                                globals()['enemies_killed'] = 0
                                # recuperar 1 coracao se não estiver no máximo
                                try:
                                    if globals().get('health', MAX_HEALTH) < MAX_HEALTH:
                                        globals()['health'] = min(MAX_HEALTH, globals().get('health', MAX_HEALTH) + 1)
                                        try:
                                            # adicionar popup de +1 Vida (posição relativa ao herói)
                                            heal_popups.append({'x': getattr(hero.actor, 'x', WIDTH//2), 'y': getattr(hero.actor, 'y', HEIGHT//2) - 40, 'timer': 60})
                                        except Exception:
                                            pass
                                        try:
                                            if sound_enabled:
                                                safe_play_sound(['heal', 'powerup'])
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        # evitar múltiplos danos no mesmo frame
                        break
                    else:
                        try:
                            # aplicar dano apenas se o herói não estiver em invulnerabilidade
                            if getattr(hero, 'hurt_timer', 0) == 0:
                                globals()['health'] = max(0, globals().get('health', MAX_HEALTH) - 1)
                                try:
                                    hero.hurt_timer = HURT_COOLDOWN
                                except Exception:
                                    pass
                                try:
                                    if sound_enabled:
                                        try:
                                            # usar fallback seguro para tocar o som de dano (hit/hurt/damage)
                                            safe_play_sound(['hurt', 'hit', 'damage'])
                                        except Exception:
                                            try:
                                                # fallback final: tentar tocar diretamente se existir
                                                attr = getattr(sounds, 'hurt', None)
                                                if attr:
                                                    attr.play()
                                            except Exception:
                                                pass
                                except Exception:
                                    pass
                                # após aplicar dano, não checar mais inimigos este frame
                                break
                        except Exception:
                            pass
            except Exception:
                pass

    # garantir remoção de inimigos marcados como mortos por segurança
    for e in enemies[:]:
        try:
            if getattr(e, 'dead', False):
                enemies.remove(e)
        except Exception:
            pass

    # câmera segue herói
    try:
        camera_x = int(max(0, min(hero.actor.x - WIDTH // 2, WORLD_WIDTH - WIDTH)))
    except Exception:
        camera_x = 0

    # proteção: se o herói caiu muito abaixo da tela (limbo), reposicionar no terreno
    try:
        if hero and getattr(hero.actor, 'y', 0) > HEIGHT + 120:
            try:
                # preservar x dentro dos limites do mundo
                hero.actor.x = max(40, min(getattr(hero.actor, 'x', 120), WORLD_WIDTH - 40))
                hero.actor.y = ground_y() - getattr(hero.actor, 'height', 32) / 2
                hero.vy = 0
                hero.on_ground = True
                hero.prev_y = hero.actor.y
            except Exception:
                pass
    except Exception:
        pass

    # spawn periódico
    spawn_timer += 1
    if spawn_timer >= SPAWN_INTERVAL:
        spawn_timer = 0
        spawn_enemy()

    # verificar condições de fim de jogo
    try:
        if globals().get('health', MAX_HEALTH) <= 0:
            globals()['state'] = 'gameover'
            globals()['in_game_menu'] = False
            return
    except Exception:
        pass
    try:
        if globals().get('coin_count', 0) >= COIN_GOAL:
            globals()['state'] = 'victory'
            globals()['in_game_menu'] = False
            return
    except Exception:
        pass


def draw():
    screen.clear()
    if state == "menu":
        try:
            ui.draw_menu(screen, menu_buttons, menu_camera_x, COIN_GOAL, WIDTH, HEIGHT, False)
        except Exception:
            screen.draw.text("MINI PLATAFORMER", center=(WIDTH // 2, 80), fontsize=56, color="white")
        return

    if state == 'menu_options':
        try:
            ui.draw_menu_options(screen, menu_options_buttons, sound_enabled, music_enabled, WIDTH, HEIGHT, menu_camera_x)
        except Exception:
            screen.draw.text('Opções', center=(WIDTH//2, 80), fontsize=44, color='white')
        return

    if state == 'gameover':
        try:
            screen.clear()
            screen.draw.text('GAME OVER', center=(WIDTH//2, HEIGHT//2 - 80), fontsize=56, color='red')
            for name, r in end_buttons.items():
                screen.draw.filled_rect(r, (40,40,80))
                label = {'restart': 'Reiniciar', 'menu': 'Voltar ao Menu'}.get(name, name)
                screen.draw.text(label, center=r.center, fontsize=22, color='white')
        except Exception:
            pass
        return

    if state == 'victory':
        try:
            screen.clear()
            screen.draw.text('PARABÉNS! Você terminou!', center=(WIDTH//2, HEIGHT//2 - 80), fontsize=40, color='gold')
            for name, r in end_buttons.items():
                screen.draw.filled_rect(r, (40,40,80))
                label = {'restart': 'Reiniciar', 'menu': 'Voltar ao Menu'}.get(name, name)
                screen.draw.text(label, center=r.center, fontsize=22, color='white')
        except Exception:
            pass
        return

    try:
        ui.draw_background(screen, images, BG_IMAGE, TERRAIN_IMAGE, WORLD_WIDTH, WIDTH, HEIGHT, camera_x)
    except Exception:
        pass

    # desenhar moedas
    for c in coins:
        try:
            frame = c.frames[int(c.frame) % len(c.frames)]
            screen.blit(frame, (c.x - camera_x - 8, c.y - 8))
        except Exception:
            pass

    # desenhar inimigos
    for e in enemies:
        try:
            ui.draw_actor_world(screen, e.actor, camera_x)
        except Exception:
            pass

    # desenhar herói
    if hero:
        try:
            ui.draw_actor_world(screen, hero.actor, camera_x)
        except Exception:
            pass

    # HUD
    try:
        ui.draw_hud(screen, images, coin_count, MAX_HEALTH, health, WIDTH)
    except Exception:
        pass

    # desenhar popups de cura
    try:
        for p in heal_popups[:]:
            try:
                screen.draw.text('+1 Vida', center=(p['x'] - camera_x, p['y']), fontsize=22, color='lightgreen')
                p['timer'] -= 1
                p['y'] -= 0.3
                if p['timer'] <= 0:
                    heal_popups.remove(p)
            except Exception:
                pass
    except Exception:
        pass

    # menu in-game (pausa) e opções in-game
    if state == 'playing' and in_game_menu:
        if globals().get('in_game_menu_state') == 'options':
            try:
                ui.draw_menu_options(screen, menu_options_buttons, sound_enabled, music_enabled, WIDTH, HEIGHT, camera_x)
            except Exception:
                try:
                    screen.draw.text('Opções (pausa)', center=(WIDTH//2, 80), fontsize=36, color='white')
                except Exception:
                    pass
            return
        try:
            # overlay escuro
            screen.draw.filled_rect(Rect(WIDTH//2 - 220, HEIGHT//2 - 120, 440, 280), (10, 10, 20))
            screen.draw.text('PAUSA', center=(WIDTH//2, HEIGHT//2 - 80), fontsize=40, color='white')
            for name, r in pause_buttons.items():
                screen.draw.filled_rect(r, (40, 40, 80))
                label = {'resume': 'Retomar', 'options': 'Opções', 'main_menu': 'Menu', 'quit': 'Sair'}.get(name, name)
                screen.draw.text(label, center=r.center, fontsize=20, color='white')
        except Exception:
            pass


def on_mouse_down(pos):
    global state, sound_enabled, music_enabled
    if state == "menu":
        for name, r in menu_buttons.items():
            if r.collidepoint(pos):
                if name == 'start':
                    start_game()
                    return
                if name == 'options':
                    state = 'menu_options'
                    return
                if name == 'quit':
                    quit()
    elif state == 'menu_options':
        for name, r in menu_options_buttons.items():
            if r.collidepoint(pos):
                if name == 'sound':
                    sound_enabled = not sound_enabled
                    return
                if name == 'music':
                    music_enabled = not music_enabled
                    try:
                        if not music_enabled:
                            music.pause()
                        else:
                            music.unpause()
                    except Exception:
                        pass
                    return
                if name == 'back':
                    state = 'menu'
                    return
    elif state == 'playing' and in_game_menu:
        # se estivermos mostrando as opções dentro da pausa, enviar os cliques para os botões de opções
        if globals().get('in_game_menu_state') == 'options':
            for name, r in menu_options_buttons.items():
                if r.collidepoint(pos):
                    if name == 'sound':
                        sound_enabled = not sound_enabled
                        return
                    if name == 'music':
                        music_enabled = not music_enabled
                        try:
                            if not music_enabled:
                                music.pause()
                            else:
                                music.unpause()
                        except Exception:
                            pass
                        return
                    if name == 'back':
                        globals()['in_game_menu_state'] = 'paused'
                        return
        
        for name, r in pause_buttons.items():
            if r.collidepoint(pos):
                if name == 'resume':
                    globals()['in_game_menu'] = False
                    return
                if name == 'options':
                    globals()['in_game_menu_state'] = 'options'
                    return
                if name == 'main_menu':
                    globals()['state'] = 'menu'
                    globals()['in_game_menu'] = False
                    return
                if name == 'quit':
                    quit()

    elif state in ('gameover', 'victory'):
        for name, r in end_buttons.items():
            if r.collidepoint(pos):
                if name == 'restart':
                    start_game()
                    return
                if name == 'menu':
                    state = 'menu'
                    return


def on_key_down(key):
    global in_game_menu
    if key == keys.ESCAPE and state == 'playing':
        in_game_menu = not in_game_menu


pgzrun.go()
