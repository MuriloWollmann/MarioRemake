import unittest

from tela_vitoria_derrota import botoes_para_tela


class TelaVitoriaDerrotaTest(unittest.TestCase):
    def test_botao_de_vitoria_pode_ser_continuar(self):
        botoes = botoes_para_tela(vitoria=True, texto_primario="[R] CONTINUAR")

        self.assertEqual(botoes[0], ("[R] CONTINUAR", True))
        self.assertEqual(botoes[1], ("[ESC] MENU PRINCIPAL", False))

    def test_botao_de_vitoria_padrao_reinicia(self):
        botoes = botoes_para_tela(vitoria=True)

        self.assertEqual(botoes[0], ("[R] JOGAR NOVAMENTE", True))


if __name__ == "__main__":
    unittest.main()
