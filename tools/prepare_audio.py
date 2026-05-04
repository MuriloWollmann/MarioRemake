from pathlib import Path
import wave


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOUND_DIR = PROJECT_ROOT / "assets" / "sounds"
DOWNLOADS_DIR = Path.home() / "Downloads"

SOUND_SOURCES = {
    "tiro.wav": "freesound_community-meaty-gunshot-101257.wav",
    "ataque_lobo.wav": "dffdv-wolf-growls-at-maurice-and-philippe-with-his-teeth-193235.wav",
    "morte_lobo.wav": "freesound_community-howl-31353.wav",
    "musica_fundo.wav": "Lobo-em-Loop.wav",
    "musica_derrota.wav": "Queda-do-Lobo.wav",
    "musica_vitoria.wav": "Lobo-Vence.wav",
}

SOUND_DURATIONS = {
    "tiro.wav": 0.9,
    "ataque_lobo.wav": 1.05,
    "morte_lobo.wav": 1.8,
    "musica_vitoria.wav": 36.0,
}


def trim_wav_start(source_path: Path, output_path: Path, max_seconds: float) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(source_path), "rb") as source:
        params = source.getparams()
        frame_count = min(source.getnframes(), int(source.getframerate() * max_seconds))
        frames = source.readframes(frame_count)

    with wave.open(str(output_path), "wb") as output:
        output.setparams(params)
        output.writeframes(frames)


def prepare_audio_assets() -> None:
    SOUND_DIR.mkdir(parents=True, exist_ok=True)

    for output_name, source_name in SOUND_SOURCES.items():
        source_path = DOWNLOADS_DIR / source_name
        output_path = SOUND_DIR / output_name

        if not source_path.exists():
            raise FileNotFoundError(f"Audio de origem nao encontrado: {source_path}")

        max_seconds = SOUND_DURATIONS.get(output_name)
        if max_seconds is None:
            output_path.write_bytes(source_path.read_bytes())
        else:
            trim_wav_start(source_path, output_path, max_seconds)

        print(f"{source_path.name} -> assets/sounds/{output_name}")


def main() -> None:
    prepare_audio_assets()
    print("Audios prontos.")


if __name__ == "__main__":
    main()
