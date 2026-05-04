import unittest

from game_logic import Bullet, GameState, update_bullets_and_damage


class GameLogicDamageTest(unittest.TestCase):
    def test_quatro_tiros_matam_o_lobo_com_quatro_vidas(self):
        state = GameState(vidas=4)
        player_box = (0.0, 0.0, 1.0, 1.0)

        for expected_lives in (3, 2, 1, 0):
            state.bullets = [Bullet(x=0.5, y=0.5, vx=0.0, vy=0.0)]
            state.invulneravel_timer = 0.0

            update_bullets_and_damage(state, 0.0, player_box)

            self.assertEqual(state.vidas, expected_lives)


if __name__ == "__main__":
    unittest.main()
