import unittest

from tools.prepare_assets import (
    HUNTER_DEATH_SHEET_FRAMES,
    HUNTER_SHEET_FRAMES,
    create_blood_frame_image,
    create_bullet_image,
    create_hunter_death_sheet_frames,
    create_hunter_sheet_frames,
    create_life_icon_image,
    remove_hunter_sheet_background,
)
import tools.prepare_assets as prepare_assets


class PrepareAssetsTest(unittest.TestCase):
    def test_usa_sprite_sheet_nova_do_cacador(self):
        self.assertEqual(
            prepare_assets.HUNTER_SHEET_SOURCE_NAME,
            "ChatGPT Image 2 de mai. de 2026, 18_38_47.png",
        )

    def test_cria_icone_de_vida_com_transparencia_e_pixels_visiveis(self):
        image = create_life_icon_image()

        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(image.size, (128, 128))

        min_alpha, max_alpha = image.getchannel("A").getextrema()
        self.assertEqual(min_alpha, 0)
        self.assertEqual(max_alpha, 255)

    def test_remove_fundo_claro_quadriculado_da_sprite_sheet_do_cacador(self):
        image = create_life_icon_image()
        image.putpixel((0, 0), (254, 254, 254, 255))
        image.putpixel((1, 0), (235, 235, 235, 255))
        image.putpixel((3, 0), (220, 220, 220, 255))
        image.putpixel((2, 0), (35, 28, 24, 255))

        cleaned = remove_hunter_sheet_background(image)

        self.assertEqual(cleaned.getpixel((0, 0))[3], 0)
        self.assertEqual(cleaned.getpixel((1, 0))[3], 0)
        self.assertEqual(cleaned.getpixel((3, 0))[3], 0)
        self.assertEqual(cleaned.getpixel((2, 0))[3], 255)

    def test_pixels_transparentes_nao_guardam_rgb_branco(self):
        make_transparent = prepare_assets.make_white_transparent
        image = create_life_icon_image()
        image.putpixel((0, 0), (255, 255, 255, 255))

        cleaned = make_transparent(image)

        self.assertEqual(cleaned.getpixel((0, 0)), (0, 0, 0, 0))

    def test_chao_tambem_remove_fundo_branco_do_jpeg(self):
        ground_names = getattr(prepare_assets, "GROUND_NAMES", None)
        should_make_transparent = getattr(prepare_assets, "should_make_white_transparent", None)

        self.assertEqual(ground_names, {"chao.png", "chao2.png", "chao3.png"})
        self.assertIsNotNone(should_make_transparent)
        for name in ground_names:
            self.assertTrue(should_make_transparent(name))

    def test_recorta_chao_verticalmente_sem_cortar_a_largura(self):
        crop_ground = getattr(prepare_assets, "crop_ground_to_visible_height", None)
        self.assertIsNotNone(crop_ground)

        image = create_life_icon_image()
        image = image.crop((0, 0, 32, 32))
        for y in range(32):
            for x in range(32):
                image.putpixel((x, y), (0, 0, 0, 0))
        for y in range(10, 20):
            for x in range(32):
                image.putpixel((x, y), (40, 80, 40, 255))

        cropped = crop_ground(image, padding=2)

        self.assertEqual(cropped.size, (32, 14))
        self.assertEqual(cropped.getchannel("A").getextrema(), (0, 255))

    def test_mapeia_os_8_frames_esperados_da_sprite_sheet_do_cacador(self):
        self.assertEqual(
            list(HUNTER_SHEET_FRAMES.keys()),
            [
                "hunter_idle1.png",
                "hunter_idle2.png",
                "hunter_idle3.png",
                "hunter_aim1.png",
                "hunter_aim2.png",
                "hunter_aim3.png",
                "hunter_shoot.png",
                "hunter_aim4.png",
            ],
        )

    def test_caixas_da_sprite_sheet_nova_preservam_cano_e_clarao(self):
        self.assertLessEqual(HUNTER_SHEET_FRAMES["hunter_idle3.png"][0], 920)
        self.assertLessEqual(HUNTER_SHEET_FRAMES["hunter_shoot.png"][0], 860)
        self.assertGreaterEqual(HUNTER_SHEET_FRAMES["hunter_shoot.png"][2], 1220)

    def test_recorta_frames_reais_do_cacador_com_transparencia_e_pixels_visiveis(self):
        frames = create_hunter_sheet_frames()

        self.assertEqual(set(frames), set(HUNTER_SHEET_FRAMES))
        for image in frames.values():
            self.assertEqual(image.mode, "RGBA")
            min_alpha, max_alpha = image.getchannel("A").getextrema()
            self.assertEqual(min_alpha, 0)
            self.assertEqual(max_alpha, 255)

    def test_cria_bala_com_transparencia_e_pixels_visiveis(self):
        image = create_bullet_image()

        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(image.size, (64, 64))
        self.assertEqual(image.getchannel("A").getextrema(), (0, 255))

    def test_mapeia_os_3_frames_esperados_da_morte_do_cacador(self):
        self.assertEqual(
            list(HUNTER_DEATH_SHEET_FRAMES.keys()),
            [
                "hunter_death1.png",
                "hunter_death2.png",
                "hunter_death3.png",
            ],
        )

    def test_recorta_frames_reais_de_morte_com_transparencia_e_pixels_visiveis(self):
        frames = create_hunter_death_sheet_frames()

        self.assertEqual(set(frames), set(HUNTER_DEATH_SHEET_FRAMES))
        for image in frames.values():
            self.assertEqual(image.mode, "RGBA")
            min_alpha, max_alpha = image.getchannel("A").getextrema()
            self.assertEqual(min_alpha, 0)
            self.assertEqual(max_alpha, 255)


if __name__ == "__main__":
    unittest.main()
