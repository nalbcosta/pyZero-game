from pygame import Rect

# Funções de desenho (utilizam os objetos globais do pgzero em runtime)
def draw_background(screen, images, BG_IMAGE, TERRAIN_IMAGE, WORLD_WIDTH, WIDTH, HEIGHT, cam_x):
    try:
        bg = images.__getattr__(BG_IMAGE)
        bw = bg.get_width()
        bh = bg.get_height()
        for y in range(-bh, HEIGHT + bh, bh):
            for x in range(-bw, WORLD_WIDTH + bw, bw):
                screen.blit(BG_IMAGE, (x - cam_x, y))
    except Exception:
        screen.fill((140, 200, 250))

    try:
        t = images.__getattr__(TERRAIN_IMAGE)
        tw = t.get_width()
        th = t.get_height()
        start = int(cam_x - (cam_x % tw)) - tw
        end = int(cam_x + WIDTH + tw)
        for x in range(start, end, tw):
            screen.blit(TERRAIN_IMAGE, (x - cam_x, HEIGHT - th))
    except Exception:
        screen.draw.filled_rect(Rect(0, HEIGHT - 40, WIDTH, 40), (60, 140, 60))


def draw_actor_world(screen, actor, camera_x):
    try:
        old = actor.pos
        actor.pos = (actor.x - camera_x, actor.y)
        actor.draw()
        actor.pos = old
    except Exception:
        try:
            screen.blit(actor.image, (actor.x - camera_x, actor.y))
        except Exception:
            pass


def draw_hud(screen, images, coin_count, MAX_HEALTH, health, WIDTH):
    try:
        screen.blit("hud_player_beige", (8, 8))
    except Exception:
        pass
    x = 80
    y = 12
    try:
        screen.blit("hud_coin", (x, y))
        x += images.hud_coin.get_width() + 6
        screen.blit("hud_character_multiply", (x, y))
        x += images.hud_character_multiply.get_width() + 6
    except Exception:
        pass
    for ch in str(coin_count):
        try:
            name = f"hud_character_{ch}"
            screen.blit(name, (x, y))
            x += images.__getattr__(name).get_width() + 2
        except Exception:
            x += 10
    hx = WIDTH - 12
    hy = 12
    for i in range(MAX_HEALTH):
        try:
            img = "hud_heart" if i < health else "hud_heart_empty"
            w = images.__getattr__(img).get_width()
            screen.blit(img, (hx - w, hy))
            hx -= w + 6
        except Exception:
            hx -= 18


def draw_menu(screen, menu_buttons, menu_camera_x, COIN_GOAL, WIDTH, HEIGHT, show_goal_message):
    # NOTE: images, BG_IMAGE, TERRAIN_IMAGE, WORLD_WIDTH are globals provided by pgzero at runtime
    try:
        draw_parallax_menu_background(screen, images, BG_IMAGE, TERRAIN_IMAGE, WORLD_WIDTH, WIDTH, HEIGHT, menu_camera_x)
    except Exception:
        pass
    screen.draw.text("MINI PLATAFORMER", center=(WIDTH // 2, 80), fontsize=56, color="white")
    for name, r in menu_buttons.items():
        screen.draw.filled_rect(r, (30, 30, 80))
        label = {
            'start': 'Iniciar',
            'options': 'Opções',
            'quit': 'Sair'
        }.get(name, name)
        screen.draw.text(label, center=r.center, fontsize=30, color="white")
    if show_goal_message:
        screen.draw.text(f"Objetivo alcançado! Você coletou {COIN_GOAL} moedas.", center=(WIDTH // 2, HEIGHT - 80), fontsize=30, color="yellow")
    screen.draw.text(f"Colete {COIN_GOAL} moedas para vencer", topleft=(12, HEIGHT - 36), fontsize=20, color="white")


def draw_menu_options(screen, menu_options_buttons, sound_enabled, music_enabled, WIDTH, HEIGHT, menu_camera_x):
    try:
        draw_parallax_menu_background(screen, images, BG_IMAGE, TERRAIN_IMAGE, WORLD_WIDTH, WIDTH, HEIGHT, menu_camera_x)
    except Exception:
        pass
    screen.draw.text("Opções", center=(WIDTH//2, 80), fontsize=44, color="white")
    screen.draw.filled_rect(menu_options_buttons['sound'], (60,60,100))
    screen.draw.text(f"Som: {'Ligado' if sound_enabled else 'Desligado'}", center=menu_options_buttons['sound'].center, fontsize=20, color="white")
    screen.draw.filled_rect(menu_options_buttons['music'], (60,60,100))
    screen.draw.text(f"Música: {'Ligada' if music_enabled else 'Desligada'}", center=menu_options_buttons['music'].center, fontsize=20, color="white")
    screen.draw.filled_rect(menu_options_buttons['back'], (80,80,120))
    screen.draw.text("Voltar", center=menu_options_buttons['back'].center, fontsize=18, color="white")

def draw_parallax_menu_background(screen, images, BG_IMAGE, TERRAIN_IMAGE, WORLD_WIDTH, WIDTH, HEIGHT, cam_x):
    """Desenha camadas em parallax para o menu: fundo distante e terreno em camadas que se movem em velocidades diferentes.
    cam_x aqui representa um offset de animação do menu (menu_camera_x)."""
    try:
        # camada distante (céu/paisagem) - movimento mais lento
        bg = images.__getattr__(BG_IMAGE)
        bw = bg.get_width()
        bh = bg.get_height()
        layer1_offset = int(cam_x * 0.25)  # parallax factor
        for x in range(-bw + (layer1_offset % bw), WORLD_WIDTH + bw, bw):
            for y in range(-bh, HEIGHT + bh, bh):
                screen.blit(BG_IMAGE, (x - layer1_offset, y))
    except Exception:
        try:
            screen.fill((140, 200, 250))
        except Exception:
            pass

    try:
        # camada intermediária (montanhas/árvores) - movimento um pouco mais rápido
        mid = images.__getattr__(BG_IMAGE)
        mw = mid.get_width()
        mh = mid.get_height()
        layer2_offset = int(cam_x * 0.6)
        for x in range(-mw + (layer2_offset % mw), WORLD_WIDTH + mw, mw):
            screen.blit(BG_IMAGE, (x - layer2_offset, HEIGHT - mh - 80))
    except Exception:
        pass

    try:
        # camada do terreno (mais próximo) - movimento mais rápido
        t = images.__getattr__(TERRAIN_IMAGE)
        tw = t.get_width()
        th = t.get_height()
        layer3_offset = int(cam_x * 1.0)
        start = int(layer3_offset - (layer3_offset % tw)) - tw
        end = int(layer3_offset + WIDTH + tw)
        for x in range(start, end, tw):
            screen.blit(TERRAIN_IMAGE, (x - layer3_offset, HEIGHT - th))
    except Exception:
        try:
            screen.draw.filled_rect(Rect(0, HEIGHT - 40, WIDTH, 40), (60, 140, 60))
        except Exception:
            pass
