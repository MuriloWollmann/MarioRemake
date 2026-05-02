import unittest

from main import (
    CHEGADA_X,
    CAMERA_LOOK_AHEAD,
    CHAO_BASE,
    CHAO_TOPO,
    CHAO_FIM,
    FULLSCREEN,
    HUNTER_DRAW_H,
    HUNTER_DRAW_W,
    PLAYER_H,
    PLAYER_W,
    WORLD_VIEW_HALF_HEIGHT,
    WORLD_VIEW_HALF_WIDTH,
    calcular_camera_x,
    calcular_hitbox_player,
)
from game_logic import HUNTER_Y
import main


class MainConfigTest(unittest.TestCase):
    def test_cacador_fica_menor_que_o_lobo(self):
        self.assertLess(HUNTER_DRAW_W, PLAYER_W)
        self.assertLess(HUNTER_DRAW_H, PLAYER_H)

    def test_fase_e_maior_que_o_mvp_curto_original(self):
        self.assertGreaterEqual(CHEGADA_X, 16.0)
        self.assertGreater(CHAO_FIM, CHEGADA_X)

    def test_jogo_abre_em_tela_cheia(self):
        self.assertTrue(FULLSCREEN)

    def test_hitbox_do_lobo_e_menor_que_o_sprite_visual(self):
        x1, y1, x2, y2 = calcular_hitbox_player(0.0, -0.85)

        self.assertGreater(x1, 0.0)
        self.assertLess(x2, PLAYER_W)
        self.assertGreater(y1, -0.90)
        self.assertLess(y2, -0.35)

    def test_camera_deixa_mais_cenario_na_frente_do_lobo(self):
        self.assertGreater(CAMERA_LOOK_AHEAD, 0.0)
        camera_x = calcular_camera_x(2.0)

        self.assertAlmostEqual(2.0 - camera_x, -CAMERA_LOOK_AHEAD)

    def test_viewport_do_mundo_mostra_mais_espaco_que_o_padrao(self):
        self.assertGreaterEqual(WORLD_VIEW_HALF_WIDTH, 1.4)
        self.assertGreaterEqual(WORLD_VIEW_HALF_HEIGHT, 1.2)

    def test_chao_visual_encosta_na_parte_de_baixo_da_camera(self):
        chao_base = getattr(main, "CHAO_BASE", None)

        self.assertIsNotNone(chao_base)
        self.assertLessEqual(chao_base, -WORLD_VIEW_HALF_HEIGHT)

    def test_chao_fica_um_pouco_mais_baixo_na_tela(self):
        self.assertLessEqual(CHAO_TOPO, -0.92)
        self.assertLess(CHAO_BASE, -WORLD_VIEW_HALF_HEIGHT)
        self.assertAlmostEqual(HUNTER_Y, CHAO_TOPO)

    def test_personagens_afundam_os_pes_na_grama(self):
        player_grass_sink = getattr(main, "PLAYER_GRASS_SINK", None)
        hunter_grass_sink = getattr(main, "HUNTER_GRASS_SINK", None)
        calcular_y_visual_player = getattr(main, "calcular_y_visual_player", None)
        calcular_y_visual_cacador = getattr(main, "calcular_y_visual_cacador", None)

        self.assertIsNotNone(player_grass_sink)
        self.assertIsNotNone(hunter_grass_sink)
        self.assertIsNotNone(calcular_y_visual_player)
        self.assertIsNotNone(calcular_y_visual_cacador)
        self.assertGreaterEqual(player_grass_sink, 0.11)
        self.assertGreaterEqual(hunter_grass_sink, 0.09)
        self.assertLess(player_grass_sink, 0.14)
        self.assertLess(hunter_grass_sink, 0.14)
        self.assertAlmostEqual(calcular_y_visual_player(CHAO_TOPO), CHAO_TOPO - player_grass_sink)
        self.assertAlmostEqual(calcular_y_visual_cacador(CHAO_TOPO), CHAO_TOPO - hunter_grass_sink)


if __name__ == "__main__":
    unittest.main()
