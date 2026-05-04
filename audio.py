from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SOUND_DIR = PROJECT_ROOT / "assets" / "sounds"

SOUND_FILES = {
    "tiro": "tiro.wav",
    "ataque_lobo": "ataque_lobo.wav",
    "morte_lobo": "morte_lobo.wav",
}
MUSIC_FILE = "musica_fundo.wav"
MUSIC_VOLUME = 0.18
DEFEAT_MUSIC_FILE = "musica_derrota.wav"
DEFEAT_MUSIC_VOLUME = 0.45
VICTORY_MUSIC_FILE = "musica_vitoria.wav"
VICTORY_MUSIC_VOLUME = 0.45


class AudioManager:
    def __init__(self, sound_dir=SOUND_DIR, enabled=True):
        self.sound_dir = Path(sound_dir)
        self.enabled = enabled
        self._pygame = None
        self._initialized = False
        self._sounds = {}

    def initialize(self):
        if self._initialized:
            return self.enabled

        self._initialized = True
        if not self.enabled:
            return False

        try:
            import pygame

            pygame.mixer.init()
            self._pygame = pygame
            for key, filename in SOUND_FILES.items():
                path = self.sound_dir / filename
                if path.exists():
                    self._sounds[key] = pygame.mixer.Sound(str(path))
        except Exception:
            self.enabled = False
            self._sounds = {}
            return False

        return bool(self._sounds)

    def play(self, key):
        if not self.enabled:
            return False

        if not self._initialized:
            self.initialize()

        sound = self._sounds.get(key)
        if sound is None:
            return False

        sound.play()
        return True

    def _play_music(self, filename, volume, loops):
        if not self.enabled:
            return False

        if not self._initialized:
            self.initialize()

        if self._pygame is None:
            return False

        path = self.sound_dir / filename
        if not path.exists():
            return False

        try:
            self._pygame.mixer.music.load(str(path))
            self._pygame.mixer.music.set_volume(volume)
            self._pygame.mixer.music.play(loops=loops)
        except Exception:
            return False

        return True

    def play_background_music(self):
        return self._play_music(MUSIC_FILE, MUSIC_VOLUME, loops=-1)

    def play_defeat_music(self):
        return self._play_music(DEFEAT_MUSIC_FILE, DEFEAT_MUSIC_VOLUME, loops=0)

    def play_victory_music(self):
        return self._play_music(VICTORY_MUSIC_FILE, VICTORY_MUSIC_VOLUME, loops=0)

    def stop_background_music(self):
        if not self.enabled or self._pygame is None:
            return False

        try:
            self._pygame.mixer.music.stop()
        except Exception:
            return False

        return True

    def shutdown(self):
        self.stop_background_music()
        if self._pygame is not None:
            try:
                self._pygame.mixer.quit()
            except Exception:
                pass

        self._pygame = None
        self._initialized = False
        self._sounds = {}


_audio = AudioManager()


def iniciar_audio():
    return _audio.initialize()


def tocar_tiro():
    return _audio.play("tiro")


def tocar_ataque_lobo():
    return _audio.play("ataque_lobo")


def tocar_morte_lobo():
    return _audio.play("morte_lobo")


def tocar_musica_fundo():
    return _audio.play_background_music()


def tocar_musica_derrota():
    return _audio.play_defeat_music()


def tocar_musica_vitoria():
    return _audio.play_victory_music()


def parar_musica_fundo():
    return _audio.stop_background_music()


def encerrar_audio():
    _audio.shutdown()
