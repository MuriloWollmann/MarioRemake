import unittest
import inspect

from main import (
    CHEGADA_X,
    CAMERA_LOOK_AHEAD,
    CHAO_BASE,
    CHAO_TOPO,
    CHAO_FIM,
    FULLSCREEN,
    HUNTER_DRAW_H,
    HUNTER_DRAW_W,
    PLAYER_ATTACK_DRAW_H,
    PLAYER_ATTACK_DRAW_W,
    PLAYER_ATTACK_DURATION,
    PLAYER_ATTACK_FRAME_TIME,
    PLAYER_H,
    PLAYER_W,
    VIDA_BAR_DRAW_H,
    VIDA_BAR_DRAW_W,
    VIDAS_INICIAIS,
    TOTAL_FASES,
    WORLD_VIEW_HALF_HEIGHT,
    WORLD_VIEW_HALF_WIDTH,
    calcular_camera_x,
    calcular_hitbox_player,
    deve_continuar_para_proxima_fase,
    player_attack_frame_index,
    texto_botao_vitoria_fase,
    vida_texture_name,
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

    def test_jogo_chama_audio_para_tiro_ataque_e_morte_do_lobo(self):
        source = inspect.getsource(main.main)

        self.assertIn("tocar_tiro()", source)
        self.assertIn("tocar_ataque_lobo()", source)
        self.assertIn("tocar_morte_lobo()", source)
        self.assertIn("tocar_musica_fundo()", source)
        self.assertIn("tocar_musica_derrota()", source)
        self.assertIn("tocar_musica_vitoria()", source)

    def test_ataque_do_lobo_usa_o_mesmo_tamanho_do_sprite_base(self):
        self.assertAlmostEqual(PLAYER_ATTACK_DRAW_W, PLAYER_W)
        self.assertAlmostEqual(PLAYER_ATTACK_DRAW_H, PLAYER_H)
        self.assertAlmostEqual(PLAYER_ATTACK_DURATION, PLAYER_ATTACK_FRAME_TIME * 3)

    def test_indice_da_animacao_de_ataque_do_lobo(self):
        self.assertEqual(player_attack_frame_index(PLAYER_ATTACK_DURATION), 0)
        self.assertEqual(player_attack_frame_index(PLAYER_ATTACK_DURATION - PLAYER_ATTACK_FRAME_TIME), 1)
        self.assertEqual(player_attack_frame_index(0.01), 2)

    def test_bandeira_real_nao_fica_espremida(self):
        flag_draw_w = getattr(main, "BANDEIRA_DRAW_W", None)
        flag_draw_h = getattr(main, "BANDEIRA_DRAW_H", None)

        self.assertIsNotNone(flag_draw_w)
        self.assertIsNotNone(flag_draw_h)
        self.assertGreaterEqual(flag_draw_w / flag_draw_h, 0.48)
        self.assertLessEqual(flag_draw_w / flag_draw_h, 0.55)

    def test_lobo_tem_4_vidas_e_morre_no_quarto_tiro(self):
        self.assertEqual(VIDAS_INICIAIS, 4)

    def test_hud_usa_barra_de_vida_em_vez_de_icones_repetidos(self):
        self.assertEqual(vida_texture_name(4), "vida4.png")
        self.assertEqual(vida_texture_name(3), "vida3.png")
        self.assertEqual(vida_texture_name(2), "vida2.png")
        self.assertEqual(vida_texture_name(1), "vida1.png")
        self.assertEqual(vida_texture_name(0), "vida1.png")
        self.assertGreater(VIDA_BAR_DRAW_W, VIDA_BAR_DRAW_H)

    def test_vitoria_intermediaria_continua_para_proxima_fase(self):
        self.assertTrue(deve_continuar_para_proxima_fase(1))
        self.assertFalse(deve_continuar_para_proxima_fase(TOTAL_FASES))
        self.assertEqual(texto_botao_vitoria_fase(1), "[R] CONTINUAR")
        self.assertEqual(texto_botao_vitoria_fase(TOTAL_FASES), "[R] JOGAR NOVAMENTE")

    def test_chegada_abre_tela_de_vitoria_antes_de_avancar_fase(self):
        source = inspect.getsource(main.main)

        self.assertIn("continuar = mostrar_tela(", source)
        self.assertIn("vitoria=True", source)
        self.assertIn("texto_primario=texto_botao_vitoria_fase(fase_atual)", source)
        self.assertLess(
            source.index("continuar = mostrar_tela("),
            source.index("avancar_para_proxima_fase("),
        )


if __name__ == "__main__":
    unittest.main()
