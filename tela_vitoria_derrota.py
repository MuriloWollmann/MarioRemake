import glfw
from OpenGL.GL import *
import math
import time
import random

# ─────────────────────────────────────────────
#  FONTE BITMAP 5×7
# ─────────────────────────────────────────────
FONTE = {
    ' ': [0x00,0x00,0x00,0x00,0x00],
    'A': [0x1F,0x24,0x44,0x24,0x1F],
    'B': [0x7F,0x49,0x49,0x49,0x36],
    'C': [0x3E,0x41,0x41,0x41,0x22],
    'D': [0x7F,0x41,0x41,0x22,0x1C],
    'E': [0x7F,0x49,0x49,0x49,0x41],
    'F': [0x7F,0x48,0x48,0x48,0x40],
    'G': [0x3E,0x41,0x41,0x49,0x2F],
    'H': [0x7F,0x08,0x08,0x08,0x7F],
    'I': [0x41,0x7F,0x41,0x00,0x00],
    'J': [0x02,0x01,0x01,0x01,0x7E],
    'K': [0x7F,0x08,0x14,0x22,0x41],
    'L': [0x7F,0x01,0x01,0x01,0x01],
    'M': [0x7F,0x20,0x10,0x20,0x7F],
    'N': [0x7F,0x10,0x08,0x04,0x7F],
    'O': [0x3E,0x41,0x41,0x41,0x3E],
    'P': [0x7F,0x48,0x48,0x48,0x30],
    'Q': [0x3E,0x41,0x45,0x42,0x3D],
    'R': [0x7F,0x48,0x4C,0x4A,0x31],
    'S': [0x32,0x49,0x49,0x49,0x26],
    'T': [0x40,0x40,0x7F,0x40,0x40],
    'U': [0x7E,0x01,0x01,0x01,0x7E],
    'V': [0x7C,0x02,0x01,0x02,0x7C],
    'W': [0x7E,0x01,0x0E,0x01,0x7E],
    'X': [0x63,0x14,0x08,0x14,0x63],
    'Y': [0x60,0x10,0x0F,0x10,0x60],
    'Z': [0x43,0x45,0x49,0x51,0x61],
    '0': [0x3E,0x45,0x49,0x51,0x3E],
    '1': [0x00,0x21,0x7F,0x01,0x00],
    '2': [0x23,0x45,0x49,0x49,0x31],
    '3': [0x22,0x41,0x49,0x49,0x36],
    '4': [0x78,0x08,0x08,0x7F,0x08],
    '5': [0x72,0x51,0x51,0x51,0x4E],
    '6': [0x1E,0x29,0x49,0x49,0x06],
    '7': [0x40,0x47,0x48,0x50,0x60],
    '8': [0x36,0x49,0x49,0x49,0x36],
    '9': [0x30,0x49,0x49,0x4A,0x3C],
    '!': [0x00,0x00,0x5F,0x00,0x00],
    '.': [0x00,0x03,0x03,0x00,0x00],
    ',': [0x00,0x03,0x04,0x00,0x00],
    '-': [0x08,0x08,0x08,0x08,0x08],
    ':': [0x00,0x36,0x36,0x00,0x00],
    '[': [0x7F,0x41,0x00,0x00,0x00],
    ']': [0x00,0x00,0x41,0x7F,0x00],
}


# ─────────────────────────────────────────────
#  HELPERS DE DESENHO
# ─────────────────────────────────────────────
def quad(x1, y1, x2, y2):
    glBegin(GL_QUADS)
    glVertex2f(x1, y1); glVertex2f(x2, y1)
    glVertex2f(x2, y2); glVertex2f(x1, y2)
    glEnd()


def tri(ax, ay, bx, by, cx, cy):
    glBegin(GL_TRIANGLES)
    glVertex2f(ax, ay); glVertex2f(bx, by); glVertex2f(cx, cy)
    glEnd()


def desenhar_pixel(cx, cy, tam):
    quad(cx, cy, cx + tam, cy + tam)


def desenhar_texto(texto, x, y, tam, r, g, b, a=1.0):
    glColor4f(r, g, b, a)
    cx = x
    for ch in texto.upper():
        cols = FONTE.get(ch, FONTE[' '])
        for ci, col in enumerate(cols):
            for row in range(7):
                if col & (1 << row):
                    desenhar_pixel(cx + ci * tam, y + row * tam, tam)
        cx += 6 * tam


def texto_larg(texto, tam):
    return len(texto) * 6 * tam


def desenhar_texto_c(texto, y, tam, r, g, b, a=1.0):
    x = -texto_larg(texto, tam) / 2
    desenhar_texto(texto, x, y, tam, r, g, b, a)


# ─────────────────────────────────────────────
#  FUNDO: FLORESTA + LUA
# ─────────────────────────────────────────────
def _circulo(cx, cy, rx, ry, segs=48):
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)
    for i in range(segs + 1):
        a = 2 * math.pi * i / segs
        glVertex2f(cx + math.cos(a) * rx, cy + math.sin(a) * ry)
    glEnd()


def desenhar_fundo(elapsed, vitoria):
    # Fundo degradê simulado
    if vitoria:
        glColor4f(0.012, 0.020, 0.060, 1.0); quad(-1, 0.0,  1, 1.0)
        glColor4f(0.020, 0.035, 0.040, 1.0); quad(-1, -0.5, 1, 0.0)
        glColor4f(0.010, 0.020, 0.010, 1.0); quad(-1, -1.0, 1, -0.5)
    else:
        glColor4f(0.008, 0.002, 0.004, 1.0); quad(-1, 0.0,  1, 1.0)
        glColor4f(0.018, 0.003, 0.005, 1.0); quad(-1, -0.5, 1, 0.0)
        glColor4f(0.010, 0.001, 0.002, 1.0); quad(-1, -1.0, 1, -0.5)

    # Lua
    if vitoria:
        lx, ly = 0.65, 0.62
        # halo
        for i in range(6):
            a = 0.10 - i * 0.015
            glColor4f(0.85, 0.72, 0.20, a)
            _circulo(lx, ly, 0.20 + i * 0.030, 0.34 + i * 0.050)
        # corpo
        glColor4f(0.92, 0.84, 0.55, 0.95)
        _circulo(lx, ly, 0.18, 0.31)
        # nuvens sobre a lua
        glColor4f(0.012, 0.020, 0.060, 0.55)
        _circulo(lx + 0.12, ly + 0.06, 0.22, 0.07)
        glColor4f(0.012, 0.020, 0.060, 0.38)
        _circulo(lx - 0.08, ly - 0.06, 0.16, 0.05)
    else:
        lx, ly = 0.60, 0.60
        glColor4f(0.35, 0.12, 0.08, 0.22)
        _circulo(lx, ly, 0.20, 0.34)
        glColor4f(0.28, 0.10, 0.06, 0.25)
        _circulo(lx, ly, 0.15, 0.26)
        # nuvens pesadas
        glColor4f(0.008, 0.002, 0.002, 0.80)
        _circulo(lx + 0.15, ly + 0.04, 0.28, 0.09)
        _circulo(lx - 0.10, ly - 0.05, 0.20, 0.07)

    _desenhar_arvores(vitoria)
    _desenhar_nevoa(elapsed, vitoria)

    if not vitoria:
        _pocao_sangue()


def _desenhar_arvores(vitoria):
    col = (0.022, 0.006, 0.008) if vitoria else (0.018, 0.002, 0.003)
    glColor3f(*col)
    posicoes = [
        (-0.95, 0.55, 0.045), (-0.80, 0.50, 0.038), (-0.65, 0.62, 0.050),
        (-0.50, 0.48, 0.035), (-0.35, 0.58, 0.042), (-0.22, 0.44, 0.032),
        (-0.10, 0.52, 0.040), ( 0.05, 0.60, 0.048), ( 0.18, 0.46, 0.034),
        ( 0.30, 0.55, 0.043), ( 0.42, 0.50, 0.037), ( 0.55, 0.64, 0.052),
        ( 0.68, 0.49, 0.036), ( 0.80, 0.57, 0.044), ( 0.92, 0.53, 0.040),
    ]
    for x, alt, larg in posicoes:
        quad(x - larg * 0.3, -1.0, x + larg * 0.3, -1.0 + alt)
        for b in range(4):
            by = -1.0 + alt * (0.25 + b * 0.18)
            d  = 1 if b % 2 == 0 else -1
            bx2, by2 = x + d * (0.12 + b * 0.03), by + 0.06
            tri(x, by, bx2, by2, bx2 + d * 0.01, by - 0.01)
            tri((x+bx2)/2, (by+by2)/2, bx2+d*0.06, by2+0.05, bx2+d*0.07, by2-0.01)


def _desenhar_nevoa(elapsed, vitoria):
    cor = (0.04, 0.06, 0.14) if vitoria else (0.06, 0.01, 0.01)
    ondas = [(-0.85, 0.08, 0.0), (-0.70, 0.06, 1.1), (-0.60, 0.07, 2.2)]
    for base_y, amp, fase in ondas:
        for i in range(20):
            t  = i / 19.0
            x  = -1.0 + t * 2.0
            y  = base_y + math.sin(elapsed * 0.4 + fase + t * 4) * amp * 0.012
            a  = 0.22 * math.sin(math.pi * t) * (0.7 + 0.3 * math.sin(elapsed * 0.6 + fase))
            glColor4f(*cor, a)
            quad(x - 0.06, y - 0.04, x + 0.06, y + 0.04)


def _pocao_sangue():
    glColor4f(0.30, 0.00, 0.00, 0.28); _circulo(0.0, -0.78, 0.28, 0.06)
    glColor4f(0.45, 0.01, 0.01, 0.18); _circulo(0.0, -0.78, 0.38, 0.10)


# ─────────────────────────────────────────────
#  PAINEL CENTRAL
# ─────────────────────────────────────────────
def desenhar_painel(elapsed, vitoria):
    pw, ph = 1.15, 0.85
    px1, py1 = -pw/2, -ph/2
    px2, py2 =  pw/2,  ph/2

    if vitoria:
        glColor4f(0.025, 0.040, 0.100, 0.90)
    else:
        glColor4f(0.060, 0.008, 0.008, 0.90)
    quad(px1, py1, px2, py2)

    pulso = 0.5 + 0.5 * math.sin(elapsed * 3.5)
    thick = 0.007
    if vitoria:
        glColor4f(0.82, 0.65, 0.15, 0.65 + 0.30 * pulso)
    else:
        glColor4f(0.75, 0.10, 0.10, 0.60 + 0.35 * pulso)
    quad(px1, py2 - thick, px2, py2)
    quad(px1, py1,         px2, py1 + thick)
    quad(px1, py1,         px1 + thick, py2)
    quad(px2 - thick, py1, px2, py2)

    # cantos diamante
    s = 0.018
    if vitoria:
        glColor4f(1.0, 0.85, 0.25, 0.8)
    else:
        glColor4f(0.9, 0.15, 0.15, 0.8)
    for cx, cy in [(px1,py1),(px2,py1),(px1,py2),(px2,py2)]:
        tri(cx, cy+s, cx+s, cy, cx, cy-s)
        tri(cx, cy+s, cx-s, cy, cx, cy-s)

    # divisória
    if vitoria:
        glColor4f(0.82, 0.65, 0.15, 0.40)
    else:
        glColor4f(0.75, 0.10, 0.10, 0.40)
    quad(-0.45, 0.035, 0.45, 0.040)

    # anéis de runa
    for i, r in enumerate([0.30, 0.40]):
        p = 0.12 + 0.08 * math.sin(elapsed * 1.8 + i * 1.5)
        if vitoria:
            glColor4f(0.82, 0.65, 0.15, p)
        else:
            glColor4f(0.75, 0.10, 0.10, p)
        segs = 48
        for s in range(segs):
            a0 = 2 * math.pi * s / segs
            a1 = 2 * math.pi * (s + 0.85) / segs
            glBegin(GL_LINES)
            glVertex2f(math.cos(a0)*r, math.sin(a0)*r*0.55 + 0.05)
            glVertex2f(math.cos(a1)*r, math.sin(a1)*r*0.55 + 0.05)
            glEnd()


# ─────────────────────────────────────────────
#  TÍTULO
# ─────────────────────────────────────────────
def desenhar_titulo(elapsed, vitoria):
    alpha = min(1.0, elapsed * 1.8)

    if vitoria:
        titulo = "VITORIA!"
        tam = 0.0072 + 0.0004 * math.sin(elapsed * 2.5)
        desenhar_texto_c(titulo, 0.185, tam * 1.02, 0.40, 0.28, 0.00, alpha * 0.6)
        desenhar_texto_c(titulo, 0.188, tam,         1.00, 0.88, 0.20, alpha)
        desenhar_texto_c(titulo, 0.190, tam * 0.98,  1.00, 0.96, 0.60,
                         alpha * (0.4 + 0.3 * math.sin(elapsed * 4)))
        # gotas de sangue abaixo das letras
        for i, bx in enumerate([-0.38, -0.22, -0.05, 0.10, 0.26, 0.40]):
            fase = elapsed * 1.1 + i * 0.9
            comp = 0.015 + 0.010 * abs(math.sin(fase * 0.5))
            vis  = 0.5 + 0.5 * math.sin(fase)
            glColor4f(0.45, 0.00, 0.00, alpha * vis * 0.8)
            quad(bx, 0.180 - comp, bx + 0.004, 0.180)

        alpha_sub = max(0.0, min(1.0, (elapsed - 0.6) * 2.0))
        desenhar_texto_c("A BESTA PREVALECEU", 0.120, 0.0026,
                         0.75, 0.60, 0.20, alpha_sub)
    else:
        titulo = "DERROTA"
        tremer = math.sin(elapsed * 18) * 0.003 if elapsed < 0.8 else 0
        tam    = 0.0070
        larg   = texto_larg(titulo, tam)
        x0     = -larg / 2 + tremer
        desenhar_texto(titulo, x0 + 0.007, 0.185 - 0.007, tam, 0.25, 0.00, 0.00, alpha * 0.7)
        desenhar_texto(titulo, x0 + 0.003, 0.185 - 0.003, tam, 0.55, 0.00, 0.00, alpha * 0.5)
        desenhar_texto(titulo, x0,         0.188,          tam, 0.90, 0.12, 0.12, alpha)
        desenhar_texto(titulo, x0 + 0.001, 0.186,          tam, 0.60, 0.05, 0.05, alpha * 0.4)

        alpha_sub = max(0.0, min(1.0, (elapsed - 0.6) * 2.0))
        desenhar_texto_c("AS TREVAS TE DEVORAM", 0.118, 0.0025,
                         0.65, 0.18, 0.18, alpha_sub)


# ─────────────────────────────────────────────
#  BOTÕES
# ─────────────────────────────────────────────
def botoes_para_tela(vitoria, texto_primario=None):
    if vitoria:
        return [
            (texto_primario or "[R] JOGAR NOVAMENTE", True),
            ("[ESC] MENU PRINCIPAL", False),
        ]

    return [
        ("[R] TENTAR NOVAMENTE", True),
        ("[ESC] MENU PRINCIPAL", False),
    ]


def desenhar_botoes(elapsed, vitoria, texto_primario=None):
    alpha = max(0.0, min(1.0, (elapsed - 1.0) * 2.0))
    if alpha <= 0:
        return

    botoes = botoes_para_tela(vitoria, texto_primario)

    for i, (texto, primario) in enumerate(botoes):
        by  = -0.14 - i * 0.10
        bw, bh = 0.72, 0.058
        bx1, by1 = -bw/2, by - bh/2
        bx2, by2 =  bw/2, by + bh/2

        if vitoria:
            glColor4f(0.18 if primario else 0.08, 0.12 if primario else 0.06,
                      0.02, (0.85 if primario else 0.70) * alpha)
        else:
            glColor4f(0.18 if primario else 0.08, 0.02, 0.02,
                      (0.85 if primario else 0.70) * alpha)
        quad(bx1, by1, bx2, by2)

        thick = 0.004
        pulso = (0.6 + 0.4 * math.sin(elapsed * 3 + i * 1.2)) if primario else 0.5
        if vitoria:
            glColor4f(0.82, 0.60, 0.12, pulso * alpha)
        else:
            glColor4f(0.75, 0.12, 0.12, pulso * alpha)
        quad(bx1, by2 - thick, bx2, by2)
        quad(bx1, by1,         bx2, by1 + thick)
        quad(bx1, by1,         bx1 + thick, by2)
        quad(bx2 - thick, by1, bx2, by2)

        tam_t = 0.0022
        tx = -texto_larg(texto, tam_t) / 2
        ty = by - 0.009
        if vitoria:
            r, g, b = (0.95, 0.80, 0.30) if primario else (0.65, 0.50, 0.20)
        else:
            r, g, b = (0.90, 0.25, 0.25) if primario else (0.60, 0.18, 0.18)
        desenhar_texto(texto, tx, ty, tam_t, r, g, b, alpha)


# ─────────────────────────────────────────────
#  PARTÍCULAS
# ─────────────────────────────────────────────

class Particula:
    __slots__ = ('x', 'y', 'vx', 'vy', 'vida', 'tempo', 'tam', 'cor')

    def __init__(self, vitoria):
        self.resetar(vitoria)

    def resetar(self, vitoria):
        self.x = random.uniform(-1.1, 1.1)
        self.y = 1.3 if vitoria else random.uniform(-0.5, 0.5)
        self.vx = random.uniform(-0.25, 0.25)
        self.vy = random.uniform(-0.6, -0.2)
        self.vida = random.uniform(2.0, 4.0)
        self.tempo = random.uniform(0, self.vida)
        self.tam = random.uniform(0.006, 0.018)

        if vitoria:
            paleta = [
                (0.90, 0.72, 0.18),
                (1.00, 0.55, 0.10),
                (0.80, 0.85, 1.00),
                (1.00, 0.92, 0.60),
            ]
        else:
            paleta = [
                (0.55, 0.02, 0.02),
                (0.30, 0.01, 0.01),
                (0.18, 0.01, 0.01),
            ]

        self.cor = random.choice(paleta)

    def update(self, dt, vitoria):
        self.tempo += dt
        self.x += self.vx * dt

        if vitoria:
            self.x += math.sin(self.tempo * 2.1) * 0.003

        self.y += self.vy * dt

        if self.tempo >= self.vida or self.y < -1.3:
            self.resetar(vitoria)

    def alpha(self):
        t = self.tempo / self.vida

        if t < 0.15:
            return t / 0.15

        if t > 0.75:
            return 1.0 - (t - 0.75) / 0.25

        return 1.0


# ─────────────────────────────────────────────
#  FUNÇÃO PRINCIPAL — USE ESSA NO mario.py
# ─────────────────────────────────────────────
def mostrar_tela(vitoria: bool, janela=None, texto_primario=None) -> bool:
    """
    Exibe a tela de vitória ou derrota com visual dark gothic.

    Args:
        vitoria (bool): True = Vitória, False = Derrota.
        janela: janela GLFW existente (opcional). Se None, cria uma nova.

    Returns:
        True  → jogador pressionou R  (reiniciar / jogar novamente)
        False → jogador pressionou ESC (menu / sair)
    """
    janela_propria = janela is None
    if janela_propria:
        if not glfw.init():
            return False
        glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
        janela = glfw.create_window(1280, 720, "Lobisomem", None, None)
        if not janela:
            glfw.terminate()
            return False
        glfw.make_context_current(janela)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    particulas = [Particula(vitoria) for _ in range(100)]
    t0 = time.time()
    tp = t0

    while not glfw.window_should_close(janela):
        agora   = time.time()
        dt      = min(agora - tp, 0.05)
        tp      = agora
        elapsed = agora - t0

        if glfw.get_key(janela, glfw.KEY_R) == glfw.PRESS:
            if janela_propria: glfw.terminate()
            return True
        if glfw.get_key(janela, glfw.KEY_ESCAPE) == glfw.PRESS:
            if janela_propria: glfw.terminate()
            return False

        for p in particulas:
            p.update(dt, vitoria)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        desenhar_fundo(elapsed, vitoria)
        desenhar_painel(elapsed, vitoria)
        desenhar_titulo(elapsed, vitoria)
        desenhar_botoes(elapsed, vitoria, texto_primario)

        for p in particulas:
            r, g, b = p.cor
            glColor4f(r, g, b, p.alpha() * 0.85)
            desenhar_pixel(p.x, p.y, p.tam)

        glfw.swap_buffers(janela)
        glfw.poll_events()

    if janela_propria:
        glfw.terminate()
    return False


# ─────────────────────────────────────────────
#  TESTE STANDALONE
#  python tela_vitoria_derrota.py vitoria
#  python tela_vitoria_derrota.py derrota
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    modo = sys.argv[1].lower() if len(sys.argv) > 1 else "vitoria"
    resultado = mostrar_tela(vitoria=(modo != "derrota"))
    print("Reiniciar:", resultado)
