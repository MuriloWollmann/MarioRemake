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
    MENU_BUTTON_DRAW_H,
    MENU_BUTTON_DRAW_W,
    MENU_STATE_NORMAL,
    MENU_STATE_PRESSING,
    MENU_STATE_SELECTED,
    MENU_STATE_START,
    MENU_PRESSED_SCALE,
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
    avancar_estado_menu,
    atualizar_pressao_menu,
    calcular_camera_x,
    calcular_hitbox_player,
    calcular_tamanho_botao_menu,
    deve_continuar_para_proxima_fase,
    menu_deve_iniciar,
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

    def test_menu_inicial_enter_seleciona_e_depois_inicia(self):
        self.assertEqual(avancar_estado_menu(MENU_STATE_NORMAL), MENU_STATE_SELECTED)
        self.assertEqual(avancar_estado_menu(MENU_STATE_SELECTED), MENU_STATE_PRESSING)
        self.assertEqual(avancar_estado_menu(MENU_STATE_PRESSING), MENU_STATE_PRESSING)
        self.assertEqual(avancar_estado_menu(MENU_STATE_START), MENU_STATE_START)
        self.assertFalse(menu_deve_iniciar(MENU_STATE_NORMAL))
        self.assertFalse(menu_deve_iniciar(MENU_STATE_SELECTED))
        self.assertFalse(menu_deve_iniciar(MENU_STATE_PRESSING))
        self.assertTrue(menu_deve_iniciar(MENU_STATE_START))

    def test_menu_so_inicia_depois_do_frame_do_botao_pressionado(self):
        estado, tempo = atualizar_pressao_menu(MENU_STATE_PRESSING, 0.08, 0.03)
        self.assertEqual(estado, MENU_STATE_PRESSING)
        self.assertGreater(tempo, 0.0)

        estado, tempo = atualizar_pressao_menu(MENU_STATE_PRESSING, tempo, 0.08)
        self.assertEqual(estado, MENU_STATE_START)
        self.assertEqual(tempo, 0.0)

    def test_botao_selecionado_do_menu_fica_sobre_o_botao_normal(self):
        self.assertGreater(MENU_BUTTON_DRAW_W, MENU_BUTTON_DRAW_H)
        self.assertGreaterEqual(MENU_BUTTON_DRAW_W, 0.72)
        self.assertGreaterEqual(MENU_BUTTON_DRAW_H, 0.20)

    def test_botao_do_menu_diminui_quando_pressionado(self):
        normal_w, normal_h = calcular_tamanho_botao_menu(pressionado=False)
        pressed_w, pressed_h = calcular_tamanho_botao_menu(pressionado=True)

        self.assertLess(MENU_PRESSED_SCALE, 1.0)
        self.assertLess(pressed_w, normal_w)
        self.assertLess(pressed_h, normal_h)
        self.assertGreater(pressed_w, normal_w * 0.85)
        self.assertGreater(pressed_h, normal_h * 0.85)

    def test_main_mostra_menu_antes_de_carregar_jogo(self):
        source = inspect.getsource(main.main)

        self.assertIn("mostrar_menu_inicial(", source)
        self.assertIn("carregar_texturas_do_jogo()", source)
        self.assertLess(
            source.index("mostrar_menu_inicial("),
            source.index("carregar_texturas_do_jogo()"),
        )


if __name__ == "__main__":
    unittest.main()
