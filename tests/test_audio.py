import tempfile
import unittest
import wave
from pathlib import Path

import audio
import tools.prepare_audio as prepare_audio


class AudioAssetsTest(unittest.TestCase):
    def test_mapeia_os_tres_sons_do_jogo(self):
        self.assertEqual(
            audio.SOUND_FILES,
            {
                "tiro": "tiro.wav",
                "ataque_lobo": "ataque_lobo.wav",
                "morte_lobo": "morte_lobo.wav",
            },
        )
        self.assertEqual(audio.MUSIC_FILE, "musica_fundo.wav")
        self.assertLessEqual(audio.MUSIC_VOLUME, 0.25)
        self.assertEqual(audio.DEFEAT_MUSIC_FILE, "musica_derrota.wav")
        self.assertLessEqual(audio.DEFEAT_MUSIC_VOLUME, 0.5)
        self.assertEqual(audio.VICTORY_MUSIC_FILE, "musica_vitoria.wav")
        self.assertLessEqual(audio.VICTORY_MUSIC_VOLUME, 0.5)

    def test_recorte_dos_sons_de_lobo_usa_so_o_inicio(self):
        self.assertLessEqual(prepare_audio.SOUND_DURATIONS["ataque_lobo.wav"], 1.1)
        self.assertLessEqual(prepare_audio.SOUND_DURATIONS["morte_lobo.wav"], 2.0)
        self.assertNotIn("musica_fundo.wav", prepare_audio.SOUND_DURATIONS)
        self.assertEqual(
            prepare_audio.SOUND_SOURCES["musica_fundo.wav"],
            "Lobo-em-Loop.wav",
        )
        self.assertNotIn("musica_derrota.wav", prepare_audio.SOUND_DURATIONS)
        self.assertEqual(
            prepare_audio.SOUND_SOURCES["musica_derrota.wav"],
            "Queda-do-Lobo.wav",
        )
        self.assertEqual(prepare_audio.SOUND_DURATIONS["musica_vitoria.wav"], 36.0)
        self.assertEqual(
            prepare_audio.SOUND_SOURCES["musica_vitoria.wav"],
            "Lobo-Vence.wav",
        )

    def test_trim_wav_start_preserva_formato_e_corta_duracao(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = temp_path / "source.wav"
            output = temp_path / "output.wav"

            with wave.open(str(source), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(1000)
                wav.writeframes(b"\x01\x00" * 3000)

            prepare_audio.trim_wav_start(source, output, max_seconds=1.25)

            with wave.open(str(output), "rb") as wav:
                self.assertEqual(wav.getnchannels(), 1)
                self.assertEqual(wav.getsampwidth(), 2)
                self.assertEqual(wav.getframerate(), 1000)
                self.assertEqual(wav.getnframes(), 1250)

    def test_audio_manager_nao_quebra_quando_desativado(self):
        manager = audio.AudioManager(enabled=False)

        self.assertFalse(manager.play("tiro"))
        self.assertFalse(manager.play("ataque_lobo"))
        self.assertFalse(manager.play("morte_lobo"))
        self.assertFalse(manager.play_background_music())
        self.assertFalse(manager.play_defeat_music())
        self.assertFalse(manager.play_victory_music())
        self.assertFalse(manager.stop_background_music())


if __name__ == "__main__":
    unittest.main()
