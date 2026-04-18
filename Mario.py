import glfw
from OpenGL.GL import *
import time
from PIL import Image
import numpy as np

# Configurações do player e física
PLAYER_W = 0.1
PLAYER_H = 0.2

GRAVIDADE = -9.8
PULO = 4.0
VEL = 0.8  # velocidade ajustada

def carregar_textura(path):
    imagem = Image.open(path)
    imagem = imagem.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = np.array(imagem.convert("RGBA"), dtype=np.uint8)

    textura = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textura)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                 imagem.width, imagem.height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    return textura

def desenhar_player(x, y):
    glColor3f(1, 0, 0)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + PLAYER_W, y)
    glVertex2f(x + PLAYER_W, y + PLAYER_H)
    glVertex2f(x, y + PLAYER_H)
    glEnd()

def desenhar_chao():
    glColor3f(0.2, 0.8, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(-1, -1)
    glVertex2f(1, -1)
    glVertex2f(1, -0.5)
    glVertex2f(-1, -0.5)
    glEnd()

def main():
    if not glfw.init():
        return

    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)

    janela = glfw.create_window(1280, 720, "Jogo", None, None)
    glfw.make_context_current(janela)

    x = 0
    y = -0.5
    vel_y = 0
    no_chao = True

    espaco_pressionado = False

    tempo_anterior = time.time()

    while not glfw.window_should_close(janela):
        glClearColor(0.5, 0.7, 1.0, 1)
        glClear(GL_COLOR_BUFFER_BIT)

        tempo_atual = time.time()
        dt = tempo_atual - tempo_anterior
        tempo_anterior = tempo_atual
        dt = min(dt, 0.05)

        if glfw.get_key(janela, glfw.KEY_D):
            x += VEL * dt

        if glfw.get_key(janela, glfw.KEY_A):
            x -= VEL * dt

        if glfw.get_key(janela, glfw.KEY_SPACE) == glfw.PRESS:
            if not espaco_pressionado and no_chao:
                vel_y = PULO
                no_chao = False
                espaco_pressionado = True
        else:
            espaco_pressionado = False

        vel_y += GRAVIDADE * dt
        y += vel_y * dt

        altura_chao = -0.5
        if y <= altura_chao:
            y = altura_chao
            vel_y = 0
            no_chao = True

        desenhar_chao()
        desenhar_player(x, y)

        glfw.swap_buffers(janela)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()