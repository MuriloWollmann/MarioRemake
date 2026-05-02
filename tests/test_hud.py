import unittest

from main import calcular_posicoes_vidas


class HudVidasTest(unittest.TestCase):
    def test_calcula_uma_posicao_para_cada_vida_no_canto_superior_esquerdo(self):
        posicoes = calcular_posicoes_vidas(3)

        self.assertEqual(
            posicoes,
            [
                (-0.95, 0.85, -0.83, 0.97),
                (-0.81, 0.85, -0.69, 0.97),
                (-0.67, 0.85, -0.55, 0.97),
            ],
        )

    def test_nao_desenha_vidas_negativas(self):
        self.assertEqual(calcular_posicoes_vidas(-2), [])


if __name__ == "__main__":
    unittest.main()
