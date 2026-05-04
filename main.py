from pathlib import Path
import random
import time


import glfw
from OpenGL.GL import *
from PIL import Image
import numpy as np

from tela_vitoria_derrota import mostrar_tela, desenhar_texto, texto_larg

from game_logic import (
    GROUND_Y,
    HUNTER_H,
    HUNTER_SHOOT_INTERVAL,
    HUNTER_TYPE_BRUTE,
    HUNTER_TYPE_GUNNER,
    HUNTER_TYPE_SCOUT,
    HUNTER_W,
    GameState,
    blood_frame_index,
    center_of_box,
    update_blood_effects,
    update_bullets_and_damage,
    update_hunters_and_spawns,
    update_player_hunter_combat,
)


PROJECT_ROOT = Path(__file__).resolve().parent
ASSET_DIR = PROJECT_ROOT / "assets"
CENARIO_ASSETS = (
    ("fundo.png", "chao.png"),
    ("fundo2.png", "chao2.png"),
    ("fundo3.png", "chao3.png"),
    ("fundo4.png", "chao4.png"),
    ("fundo5.png", "chao5.png"),
)
FULLSCREEN = True
WINDOWED_WIDTH = 1280
WINDOWED_HEIGHT = 720
CAMERA_LOOK_AHEAD = 0.45
WORLD_VIEW_HALF_WIDTH = 1.45
WORLD_VIEW_HALF_HEIGHT = 1.25
HUD_VIEW_HALF_WIDTH = 1.0
HUD_VIEW_HALF_HEIGHT = 1.0

# Configuracoes do player e fisica
PLAYER_W = 0.5
PLAYER_H = 0.5

GRAVIDADE = -9.8
PULO = 4.0
VEL = 0.8

# Mundo
CHAO_INICIO = -5
CHAO_FIM = 24

# Chegada
CHEGADA_X = 18.0

# O topo do chao fica aqui; player pousa nessa linha
CHAO_TOPO = GROUND_Y
CHAO_BASE = -WORLD_VIEW_HALF_HEIGHT - 0.08

# Animacao
ANIM_FPS = 0.12

# HUD
VIDAS_INICIAIS = 3
HUD_VIDA_TAMANHO = 0.12
HUD_VIDA_ESPACAMENTO = 0.02
HUD_VIDA_X = -0.95
HUD_VIDA_TOPO = 0.97
HUD_FASE_TAMANHO = 0.003
HUD_FASE_DIREITA = 0.95
HUD_FASE_Y = 0.88

BULLET_DRAW_SIZE = 0.08
HUNTER_DEATH_DRAW_W = 0.62
HUNTER_DEATH_DRAW_H = 0.46
HUNTER_AIM_WINDOW = 0.45
HUNTER_DRAW_W = 0.30
HUNTER_DRAW_H = 0.40
HUNTER_DRAW_SIZES = {
    HUNTER_TYPE_GUNNER: (HUNTER_DRAW_W, HUNTER_DRAW_H),
    HUNTER_TYPE_SCOUT: (0.26, 0.37),
    HUNTER_TYPE_BRUTE: (0.38, 0.47),
}
PLAYER_GRASS_SINK = 0.12
HUNTER_GRASS_SINK = 0.10
PLAYER_HITBOX_MARGIN_X = 0.12
PLAYER_HITBOX_BOTTOM_MARGIN = 0.07
PLAYER_HITBOX_TOP_MARGIN = 0.16


class AssetError(RuntimeError):
    pass


def asset_path(name):
    path = ASSET_DIR / name
    if not path.exists():
        raise AssetError(
            f"Asset ausente: {path}\n"
            "Rode primeiro: python tools/prepare_assets.py"
        )
    return path


def carregar_textura(name, repeat_x=False, repeat_y=False):
    path = asset_path(name)

    with Image.open(path) as imagem:
        imagem = imagem.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = np.array(imagem.convert("RGBA"), dtype=np.uint8)
        width, height = imagem.width, imagem.height

    id_textura = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, id_textura)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT if repeat_x else GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT if repeat_y else GL_CLAMP_TO_EDGE)
    return id_textura


def desenhar_quad_texturizado(x1, y1, x2, y2, tex_x1=0.0, tex_y1=0.0, tex_x2=1.0, tex_y2=1.0):
    glBegin(GL_QUADS)
    glTexCoord2f(tex_x1, tex_y1)
    glVertex2f(x1, y1)
    glTexCoord2f(tex_x2, tex_y1)
    glVertex2f(x2, y1)
    glTexCoord2f(tex_x2, tex_y2)
    glVertex2f(x2, y2)
    glTexCoord2f(tex_x1, tex_y2)
    glVertex2f(x1, y2)
    glEnd()


def desenhar_fundo(tex_fundo, camera_x):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_fundo)
    glColor3f(1, 1, 1)

    offset = (camera_x * 0.2) % 2.0
    tex_x1 = offset / 2.0
    tex_x2 = tex_x1 + 1.0

    desenhar_quad_texturizado(
        -WORLD_VIEW_HALF_WIDTH,
        -WORLD_VIEW_HALF_HEIGHT,
        WORLD_VIEW_HALF_WIDTH,
        WORLD_VIEW_HALF_HEIGHT,
        tex_x1,
        0.0,
        tex_x2,
        1.0,
    )

    glDisable(GL_TEXTURE_2D)


def desenhar_chao(tex_chao, camera_x):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_chao)
    glColor3f(1, 1, 1)

    x_inicio_tela = CHAO_INICIO - camera_x
    x_fim_tela = CHAO_FIM - camera_x

    largura_mundo = CHAO_FIM - CHAO_INICIO
    repeticoes = largura_mundo / 0.6

    uv_y1 = 0.0
    uv_y2 = 1.0

    desenhar_quad_texturizado(x_inicio_tela, CHAO_BASE, x_fim_tela, CHAO_TOPO, 0, uv_y1, repeticoes, uv_y2)

    glDisable(GL_TEXTURE_2D)


def calcular_y_visual_player(y):
    return y - PLAYER_GRASS_SINK


def calcular_y_visual_cacador(y):
    return y - HUNTER_GRASS_SINK


def tamanho_desenho_cacador(enemy_type):
    return HUNTER_DRAW_SIZES.get(enemy_type, HUNTER_DRAW_SIZES[HUNTER_TYPE_GUNNER])


def desenhar_player(frames_run, frames_jump, tex_idle, x, y, no_chao, movendo, virado_esquerda, frame_anim):
    glEnable(GL_TEXTURE_2D)
    glColor3f(1, 1, 1)

    if not no_chao:
        sequencia = [0, 1, 2, 0]
        idx = sequencia[frame_anim % len(sequencia)]
        glBindTexture(GL_TEXTURE_2D, frames_jump[idx])
    elif movendo:
        sequencia = [0, 1, 2, 1]
        idx = sequencia[frame_anim % len(sequencia)]
        glBindTexture(GL_TEXTURE_2D, frames_run[idx])
    else:
        glBindTexture(GL_TEXTURE_2D, tex_idle)

    visual_y = calcular_y_visual_player(y)
    if virado_esquerda:
        desenhar_quad_texturizado(x + PLAYER_W, visual_y, x, visual_y + PLAYER_H)
    else:
        desenhar_quad_texturizado(x, visual_y, x + PLAYER_W, visual_y + PLAYER_H)

    glDisable(GL_TEXTURE_2D)


def desenhar_chegada(tex_bandeira, x_mundo, camera_x):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_bandeira)
    glColor3f(1, 1, 1)

    x_tela = x_mundo - camera_x

    desenhar_quad_texturizado(x_tela, CHAO_TOPO, x_tela + 0.2, CHAO_TOPO + 0.8)

    glDisable(GL_TEXTURE_2D)


def calcular_posicoes_vidas(vidas):
    posicoes = []
    quantidade = max(0, vidas)
    y2 = HUD_VIDA_TOPO
    y1 = y2 - HUD_VIDA_TAMANHO

    for indice in range(quantidade):
        x1 = HUD_VIDA_X + indice * (HUD_VIDA_TAMANHO + HUD_VIDA_ESPACAMENTO)
        x2 = x1 + HUD_VIDA_TAMANHO
        posicoes.append((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))

    return posicoes


def desenhar_hud_vidas(tex_vida, vidas):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_vida)
    glColor3f(1, 1, 1)

    for x1, y1, x2, y2 in calcular_posicoes_vidas(vidas):
        desenhar_quad_texturizado(x1, y1, x2, y2)

    glDisable(GL_TEXTURE_2D)


def texto_fase(fase):
    return f"FASE {max(1, int(fase))}"


def calcular_posicao_hud_fase(fase):
    texto = texto_fase(fase)
    x = HUD_FASE_DIREITA - texto_larg(texto, HUD_FASE_TAMANHO)
    return (round(x, 3), HUD_FASE_Y)


def desenhar_hud_fase(fase):
    glDisable(GL_TEXTURE_2D)
    texto = texto_fase(fase)
    x, y = calcular_posicao_hud_fase(fase)

    desenhar_texto(texto, x + 0.004, y - 0.004, HUD_FASE_TAMANHO, 0.0, 0.0, 0.0, 0.55)
    desenhar_texto(texto, x, y, HUD_FASE_TAMANHO, 1.0, 0.92, 0.55, 1.0)


def calcular_hitbox_player(x, y):
    visual_y1 = calcular_y_visual_player(y)
    visual_y2 = visual_y1 + PLAYER_H
    return (
        x + PLAYER_HITBOX_MARGIN_X,
        visual_y1 + PLAYER_HITBOX_BOTTOM_MARGIN,
        x + PLAYER_W - PLAYER_HITBOX_MARGIN_X,
        visual_y2 - PLAYER_HITBOX_TOP_MARGIN,
    )


def calcular_camera_x(player_x):
    return max(0.0, player_x + CAMERA_LOOK_AHEAD)


def selecionar_textura_cacador(hunter, tex_hunter_idle, tex_hunter_aim=None, tex_hunter_shoot=None, frame_anim=0):
    if isinstance(tex_hunter_idle, dict):
        texturas = tex_hunter_idle.get(hunter.enemy_type, tex_hunter_idle[HUNTER_TYPE_GUNNER])
        tex_hunter_idle = texturas["idle"]
        tex_hunter_aim = texturas["aim"]
        tex_hunter_shoot = texturas["shoot"]

    if hunter.shoot_flash > 0:
        return tex_hunter_shoot

    if hunter.shoot_timer >= HUNTER_SHOOT_INTERVAL - HUNTER_AIM_WINDOW:
        return tex_hunter_aim[frame_anim % len(tex_hunter_aim)]

    return tex_hunter_idle[frame_anim % len(tex_hunter_idle)]


def desenhar_cacadores(hunters, texturas_inimigos, camera_x, frame_anim):
    glEnable(GL_TEXTURE_2D)
    glColor3f(1, 1, 1)

    for hunter in hunters:
        glBindTexture(
            GL_TEXTURE_2D,
            selecionar_textura_cacador(hunter, texturas_inimigos, frame_anim=frame_anim),
        )

        draw_w, draw_h = tamanho_desenho_cacador(hunter.enemy_type)
        x_tela = hunter.x - camera_x - (draw_w - HUNTER_W) / 2
        visual_y = calcular_y_visual_cacador(hunter.y)
        desenhar_quad_texturizado(x_tela, visual_y, x_tela + draw_w, visual_y + draw_h)

    glDisable(GL_TEXTURE_2D)


def desenhar_balas(bullets, tex_bullet, camera_x):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_bullet)
    glColor3f(1, 1, 1)

    half = BULLET_DRAW_SIZE / 2
    for bullet in bullets:
        x_tela = bullet.x - camera_x
        desenhar_quad_texturizado(x_tela - half, bullet.y - half, x_tela + half, bullet.y + half)

    glDisable(GL_TEXTURE_2D)


def desenhar_mortes_cacador(effects, tex_hunter_death, camera_x):
    glEnable(GL_TEXTURE_2D)
    glColor3f(1, 1, 1)

    for effect in effects:
        glBindTexture(GL_TEXTURE_2D, tex_hunter_death[blood_frame_index(effect)])
        x_tela = effect.x - camera_x - 0.16
        visual_y = calcular_y_visual_cacador(effect.y)
        desenhar_quad_texturizado(x_tela, visual_y, x_tela + HUNTER_DEATH_DRAW_W, visual_y + HUNTER_DEATH_DRAW_H)

    glDisable(GL_TEXTURE_2D)


def escolher_indice_cenario(fase, total_cenarios, indice_atual=None):
    if total_cenarios <= 0:
        raise ValueError("E preciso ter pelo menos um cenario.")

    if fase <= 1 or indice_atual is None:
        return 0

    opcoes = [indice for indice in range(total_cenarios) if indice != indice_atual]
    return random.choice(opcoes or [indice_atual])


def criar_estado_fase(vidas, fase):
    return GameState(vidas=vidas, nivel=fase)


def carregar_texturas_inimigo(prefix):
    return {
        "idle": [
            carregar_textura(f"{prefix}_idle1.png"),
            carregar_textura(f"{prefix}_idle2.png"),
            carregar_textura(f"{prefix}_idle3.png"),
        ],
        "aim": [
            carregar_textura(f"{prefix}_aim1.png"),
            carregar_textura(f"{prefix}_aim2.png"),
            carregar_textura(f"{prefix}_aim3.png"),
            carregar_textura(f"{prefix}_aim4.png"),
        ],
        "shoot": carregar_textura(f"{prefix}_shoot.png"),
    }


def carregar_texturas_do_jogo():
    cenarios = [
        (
            carregar_textura(fundo, repeat_x=True),
            carregar_textura(chao, repeat_x=True),
        )
        for fundo, chao in CENARIO_ASSETS
    ]
    tex_bandeira = carregar_textura("bandeira.png")
    tex_vida = carregar_textura("vida.png")
    tex_idle = carregar_textura("player.png")
    texturas_inimigos = {
        HUNTER_TYPE_GUNNER: carregar_texturas_inimigo("hunter"),
        HUNTER_TYPE_SCOUT: carregar_texturas_inimigo("hunter_scout"),
        HUNTER_TYPE_BRUTE: carregar_texturas_inimigo("hunter_brute"),
    }
    tex_bullet = carregar_textura("bullet.png")
    tex_hunter_death = [
        carregar_textura("hunter_death1.png"),
        carregar_textura("hunter_death2.png"),
        carregar_textura("hunter_death3.png"),
    ]

    frames_run = [
        carregar_textura("Run.png"),
        carregar_textura("Run2.png"),
        carregar_textura("Run3.png"),
    ]
    frames_jump = [
        carregar_textura("Jump.png"),
        carregar_textura("Jump2.png"),
        carregar_textura("Jump3.png"),
    ]

    return (
        cenarios,
        tex_bandeira,
        tex_vida,
        tex_idle,
        frames_run,
        frames_jump,
        texturas_inimigos,
        tex_bullet,
        tex_hunter_death,
    )


def configurar_projecao(left, right, bottom, top):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(left, right, bottom, top, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def configurar_projecao_mundo():
    configurar_projecao(
        -WORLD_VIEW_HALF_WIDTH,
        WORLD_VIEW_HALF_WIDTH,
        -WORLD_VIEW_HALF_HEIGHT,
        WORLD_VIEW_HALF_HEIGHT,
    )


def configurar_projecao_hud():
    configurar_projecao(
        -HUD_VIEW_HALF_WIDTH,
        HUD_VIEW_HALF_WIDTH,
        -HUD_VIEW_HALF_HEIGHT,
        HUD_VIEW_HALF_HEIGHT,
    )


def criar_janela_jogo():
    if FULLSCREEN:
        monitor = glfw.get_primary_monitor()
        if monitor:
            video_mode = glfw.get_video_mode(monitor)
            if video_mode:
                return glfw.create_window(
                    video_mode.size.width,
                    video_mode.size.height,
                    "Jogo",
                    monitor,
                    None,
                )

    return glfw.create_window(WINDOWED_WIDTH, WINDOWED_HEIGHT, "Jogo", None, None)


def main():
    if not glfw.init():
        print("Erro ao inicializar GLFW.")
        return

    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)

    janela = criar_janela_jogo()
    if not janela:
        glfw.terminate()
        print("Erro ao criar janela GLFW.")
        return

    glfw.make_context_current(janela)
    framebuffer_w, framebuffer_h = glfw.get_framebuffer_size(janela)
    glViewport(0, 0, framebuffer_w, framebuffer_h)
    glfw.swap_interval(1)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    try:
        (
            cenarios,
            tex_bandeira,
            tex_vida,
            tex_idle,
            frames_run,
            frames_jump,
            texturas_inimigos,
            tex_bullet,
            tex_hunter_death,
        ) = carregar_texturas_do_jogo()
    except AssetError as exc:
        print(exc)
        glfw.terminate()
        return

    fase_atual = 1
    indice_cenario = escolher_indice_cenario(fase_atual, len(cenarios))
    estado_jogo = criar_estado_fase(VIDAS_INICIAIS, fase_atual)
    glfw.set_window_title(janela, f"Jogo - Fase {fase_atual}")

    x = 0.0
    y = CHAO_TOPO
    vel_y = 0.0
    no_chao = True

    camera_x = 0.0

    espaco_pressionado = False
    virado_esquerda = False
    frame_anim = 0
    tempo_anim = 0.0

    tempo_anterior = time.time()

    while not glfw.window_should_close(janela):
        glClearColor(0.5, 0.7, 1.0, 1)
        glClear(GL_COLOR_BUFFER_BIT)

        tempo_atual = time.time()
        dt = tempo_atual - tempo_anterior
        tempo_anterior = tempo_atual
        dt = min(dt, 0.05)

        movendo = False

        if glfw.get_key(janela, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(janela, True)

        if glfw.get_key(janela, glfw.KEY_D) == glfw.PRESS:
            x += VEL * dt
            virado_esquerda = False
            movendo = True

        if glfw.get_key(janela, glfw.KEY_A) == glfw.PRESS:
            x -= VEL * dt
            virado_esquerda = True
            movendo = True

        if glfw.get_key(janela, glfw.KEY_SPACE) == glfw.PRESS:
            if not espaco_pressionado and no_chao:
                vel_y = PULO
                no_chao = False
                espaco_pressionado = True
                frame_anim = 0
                tempo_anim = 0.0
        else:
            espaco_pressionado = False

        vel_y += GRAVIDADE * dt
        y += vel_y * dt

        if y <= CHAO_TOPO:
            y = CHAO_TOPO
            vel_y = 0
            no_chao = True

        tempo_anim += dt
        if tempo_anim >= ANIM_FPS:
            tempo_anim -= ANIM_FPS
            frame_anim += 1

        camera_x = calcular_camera_x(x)

        x_tela = x - camera_x
        if x_tela < -WORLD_VIEW_HALF_WIDTH:
            x = camera_x - WORLD_VIEW_HALF_WIDTH

        if x >= CHEGADA_X:
            fase_atual += 1
            indice_cenario = escolher_indice_cenario(fase_atual, len(cenarios), indice_cenario)
            estado_jogo = criar_estado_fase(estado_jogo.vidas, fase_atual)
            glfw.set_window_title(janela, f"Jogo - Fase {fase_atual}")

            x = 0.0
            y = CHAO_TOPO
            vel_y = 0.0
            no_chao = True
            camera_x = 0.0
            espaco_pressionado = False
            virado_esquerda = False
            frame_anim = 0
            tempo_anim = 0.0
            tempo_anterior = time.time()
            continue

        player_box = calcular_hitbox_player(x, y)
        player_center = center_of_box(player_box)

        update_hunters_and_spawns(estado_jogo, dt, camera_x, player_center, level=fase_atual)
        update_player_hunter_combat(estado_jogo, player_box)
        update_bullets_and_damage(estado_jogo, dt, player_box)
        update_blood_effects(estado_jogo, dt)

        tex_fundo, tex_chao = cenarios[indice_cenario]

        configurar_projecao_mundo()
        desenhar_fundo(tex_fundo, camera_x)
        desenhar_chao(tex_chao, camera_x)
        desenhar_chegada(tex_bandeira, CHEGADA_X, camera_x)
        desenhar_mortes_cacador(estado_jogo.blood_effects, tex_hunter_death, camera_x)
        desenhar_cacadores(estado_jogo.hunters, texturas_inimigos, camera_x, frame_anim)
        desenhar_balas(estado_jogo.bullets, tex_bullet, camera_x)
        desenhar_player(frames_run, frames_jump, tex_idle, x - camera_x, y, no_chao, movendo, virado_esquerda, frame_anim)

        configurar_projecao_hud()
        desenhar_hud_vidas(tex_vida, estado_jogo.vidas)
        desenhar_hud_fase(fase_atual)

        glfw.swap_buffers(janela)
        glfw.poll_events()



        if estado_jogo.vidas <= 0:
             reiniciar = mostrar_tela(vitoria=False, janela=janela)

             if reiniciar:
                glfw.destroy_window(janela)
                glfw.terminate()
                main()
                return

             else:
                glfw.set_window_should_close(janela, True)

    glfw.terminate()


if __name__ == "__main__":
    main()
