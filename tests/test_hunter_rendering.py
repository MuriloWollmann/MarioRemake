import unittest

from game_logic import HUNTER_SHOOT_INTERVAL, Hunter
from main import selecionar_textura_cacador


class HunterRenderingTest(unittest.TestCase):
    def test_seleciona_frame_idle_quando_cacador_nao_esta_mirando(self):
        hunter = Hunter(x=0.0, shoot_timer=0.2)

        textura = selecionar_textura_cacador(
            hunter,
            tex_hunter_idle=["idle1", "idle2", "idle3"],
            tex_hunter_aim=["aim1", "aim2", "aim3", "aim4"],
            tex_hunter_shoot="shoot",
            frame_anim=4,
        )

        self.assertEqual(textura, "idle2")

    def test_seleciona_frame_aim_quando_disparo_esta_proximo(self):
        hunter = Hunter(x=0.0, shoot_timer=HUNTER_SHOOT_INTERVAL - 0.25)

        textura = selecionar_textura_cacador(
            hunter,
            tex_hunter_idle=["idle1", "idle2", "idle3"],
            tex_hunter_aim=["aim1", "aim2", "aim3", "aim4"],
            tex_hunter_shoot="shoot",
            frame_anim=6,
        )

        self.assertEqual(textura, "aim3")

    def test_seleciona_frame_shoot_durante_flash_de_disparo(self):
        hunter = Hunter(x=0.0, shoot_flash=0.1)

        textura = selecionar_textura_cacador(
            hunter,
            tex_hunter_idle=["idle1", "idle2", "idle3"],
            tex_hunter_aim=["aim1", "aim2", "aim3", "aim4"],
            tex_hunter_shoot="shoot",
            frame_anim=0,
        )

        self.assertEqual(textura, "shoot")


if __name__ == "__main__":
    unittest.main()
