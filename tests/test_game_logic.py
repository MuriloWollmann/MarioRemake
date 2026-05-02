import math
import unittest

from game_logic import (
    BULLET_RADIUS,
    BULLET_SPEED,
    GROUND_Y,
    HUNTER_Y,
    HUNTER_SPAWN_AHEAD,
    SPAWN_INTERVAL,
    MAX_HUNTERS,
    GameState,
    Hunter,
    Bullet,
    PLAYER_HITBOX,
    update_bullets_and_damage,
    update_hunters_and_spawns,
    update_player_hunter_combat,
)


class GameLogicTest(unittest.TestCase):
    def test_balas_sao_mais_lentas_e_com_raio_menor_para_dar_tempo_de_desviar(self):
        self.assertLessEqual(BULLET_SPEED, 0.9)
        self.assertLessEqual(BULLET_RADIUS, 0.03)

    def test_intervalo_de_spawn_e_6_segundos(self):
        self.assertEqual(SPAWN_INTERVAL, 6.0)

    def test_cacador_usa_linha_do_chao_rebaixada(self):
        self.assertLessEqual(GROUND_Y, -0.92)
        self.assertEqual(HUNTER_Y, GROUND_Y)

    def test_cacador_nasce_visivel_perto_da_borda_direita(self):
        self.assertGreaterEqual(HUNTER_SPAWN_AHEAD, 1.15)
        self.assertLessEqual(HUNTER_SPAWN_AHEAD, 1.35)

    def test_cacador_nasce_depois_de_6s_na_frente_da_camera(self):
        state = GameState()

        update_hunters_and_spawns(state, dt=SPAWN_INTERVAL - 0.1, camera_x=4.0, player_center=(4.25, -0.6))
        self.assertEqual(state.hunters, [])

        update_hunters_and_spawns(state, dt=0.1, camera_x=4.0, player_center=(4.25, -0.6))

        self.assertEqual(len(state.hunters), 1)
        self.assertAlmostEqual(state.hunters[0].x, 4.0 + HUNTER_SPAWN_AHEAD)

    def test_limita_no_maximo_3_cacadores_vivos(self):
        state = GameState(
            hunters=[Hunter(x=float(i), y=-0.85) for i in range(MAX_HUNTERS)]
        )

        update_hunters_and_spawns(state, dt=SPAWN_INTERVAL + 0.1, camera_x=2.0, player_center=(2.25, -0.6))

        self.assertEqual(len(state.hunters), MAX_HUNTERS)

    def test_tiro_mira_na_posicao_do_player_no_momento_do_disparo(self):
        state = GameState(hunters=[Hunter(x=3.0, y=-0.85, shoot_timer=1.39)])

        update_hunters_and_spawns(state, dt=0.01, camera_x=0.0, player_center=(0.25, -0.2))

        self.assertEqual(len(state.bullets), 1)
        bullet = state.bullets[0]
        self.assertAlmostEqual(math.hypot(bullet.vx, bullet.vy), BULLET_SPEED)
        self.assertLess(bullet.vx, 0)
        self.assertGreater(bullet.vy, 0)

    def test_bala_que_acerta_tira_uma_vida_e_some(self):
        state = GameState(
            vidas=3,
            bullets=[Bullet(x=0.25, y=-0.6, vx=0.0, vy=0.0)],
        )

        update_bullets_and_damage(state, dt=0.1, player_box=PLAYER_HITBOX)

        self.assertEqual(state.vidas, 2)
        self.assertEqual(state.bullets, [])
        self.assertGreater(state.invulneravel_timer, 0)

    def test_invulnerabilidade_impede_dano_duplicado_imediato(self):
        state = GameState(
            vidas=3,
            invulneravel_timer=1.0,
            bullets=[Bullet(x=0.25, y=-0.6, vx=0.0, vy=0.0)],
        )

        update_bullets_and_damage(state, dt=0.1, player_box=PLAYER_HITBOX)

        self.assertEqual(state.vidas, 3)
        self.assertEqual(state.bullets, [])

    def test_lobo_perto_remove_cacador_e_cria_sangue(self):
        state = GameState(hunters=[Hunter(x=0.2, y=-0.85)])

        update_player_hunter_combat(state, player_box=PLAYER_HITBOX)

        self.assertEqual(state.hunters, [])
        self.assertEqual(len(state.blood_effects), 1)
        self.assertAlmostEqual(state.blood_effects[0].x, 0.2)


if __name__ == "__main__":
    unittest.main()
