from pathlib import Path
from collections import deque

from PIL import Image, ImageDraw


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = PROJECT_ROOT / "assets"
DOWNLOADS_DIR = Path.home() / "Downloads"
HUNTER_SHEET_SOURCE_NAME = "ChatGPT Image 2 de mai. de 2026, 18_38_47.png"
HUNTER_SHEET_PATH = DOWNLOADS_DIR / HUNTER_SHEET_SOURCE_NAME
HUNTER_DEATH_SHEET_SOURCE_NAME = "ChatGPT Image 2 de mai. de 2026, 18_07_18.png"
HUNTER_DEATH_SHEET_PATH = DOWNLOADS_DIR / HUNTER_DEATH_SHEET_SOURCE_NAME
PLAYER_ATTACK_SHEET_SOURCE_NAME = "ChatGPT Image 3 de mai. de 2026, 15_48_16.png"
PLAYER_ATTACK_SHEET_PATH = DOWNLOADS_DIR / PLAYER_ATTACK_SHEET_SOURCE_NAME
FLAG_SOURCE_NAME = "ChatGPT Image 3 de mai. de 2026, 16_26_10.png"
FLAG_SOURCE_PATH = DOWNLOADS_DIR / FLAG_SOURCE_NAME
HEALTH_BAR_SOURCE_NAME = "ChatGPT Image 3 de mai. de 2026, 22_21_29.png"
HEALTH_BAR_SOURCE_PATH = DOWNLOADS_DIR / HEALTH_BAR_SOURCE_NAME
MENU_BACKGROUND_SOURCE_NAME = "ChatGPT Image 3 de mai. de 2026, 22_42_54.png"
MENU_BACKGROUND_SOURCE_PATH = DOWNLOADS_DIR / MENU_BACKGROUND_SOURCE_NAME
MENU_SELECTED_BUTTON_SOURCE_NAME = "ChatGPT Image 3 de mai. de 2026, 22_45_49.png"
MENU_SELECTED_BUTTON_SOURCE_PATH = DOWNLOADS_DIR / MENU_SELECTED_BUTTON_SOURCE_NAME
HUNTER_SHEET_CROP_MARGIN = 8


HUNTER_SHEET_FRAMES = {
    "hunter_idle1.png": (142, 95, 360, 415),
    "hunter_idle2.png": (548, 95, 735, 410),
    "hunter_idle3.png": (910, 95, 1160, 415),
    "hunter_aim1.png": (1285, 98, 1568, 418),
    "hunter_aim2.png": (110, 490, 382, 805),
    "hunter_aim3.png": (495, 493, 773, 806),
    "hunter_shoot.png": (855, 498, 1222, 806),
    "hunter_aim4.png": (1302, 494, 1575, 806),
}


HUNTER_DEATH_SHEET_FRAMES = {
    "hunter_death1.png": (97, 78, 637, 591),
    "hunter_death2.png": (718, 259, 1282, 595),
    "hunter_death3.png": (1399, 427, 2096, 618),
}


PLAYER_ATTACK_SHEET_FRAMES = {
    "Attack.png": (73, 400, 447, 661),
    "Attack2.png": (488, 423, 965, 663),
    "Attack3.png": (965, 445, 1401, 662),
}


HEALTH_BAR_SHEET_FRAMES = {
    "vida4.png": (42, 371, 474, 462),
    "vida3.png": (512, 372, 941, 462),
    "vida2.png": (978, 372, 1404, 462),
    "vida1.png": (1444, 372, 1873, 462),
}


SOURCE_ASSETS = {
    # Default green scenario.
    "fundo.png": "WhatsApp Image 2026-05-02 at 17.21.33 (1).jpeg",
    "chao.png": "WhatsApp Image 2026-05-02 at 17.21.33.jpeg",
    # Optional scenario variations.
    "fundo2.png": "WhatsApp Image 2026-05-02 at 17.21.33 (2).jpeg",
    "chao2.png": "WhatsApp Image 2026-05-02 at 17.21.31.jpeg",
    "fundo3.png": "WhatsApp Image 2026-05-02 at 17.21.31 (2).jpeg",
    "chao3.png": "WhatsApp Image 2026-05-02 at 17.21.31 (1).jpeg",
    # Player frames.
    "player.png": "WhatsApp Image 2026-05-02 at 17.21.32 (1).jpeg",
    "Run.png": "WhatsApp Image 2026-05-02 at 17.21.34.jpeg",
    "Run2.png": "WhatsApp Image 2026-05-02 at 17.21.32 (3).jpeg",
    "Run3.png": "WhatsApp Image 2026-05-02 at 17.21.32 (2).jpeg",
    "Jump.png": "WhatsApp Image 2026-05-02 at 17.21.32.jpeg",
    "Jump2.png": "WhatsApp Image 2026-05-02 at 17.21.31 (4).jpeg",
    "Jump3.png": "WhatsApp Image 2026-05-02 at 17.21.31 (3).jpeg",
}


SPRITE_NAMES = {
    "player.png",
    "Run.png",
    "Run2.png",
    "Run3.png",
    "Jump.png",
    "Jump2.png",
    "Jump3.png",
}


GROUND_NAMES = {"chao.png", "chao2.png", "chao3.png"}


def should_make_white_transparent(output_name: str) -> bool:
    return output_name in SPRITE_NAMES or output_name in GROUND_NAMES


def make_white_transparent(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()

    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = pixels[x, y]
            near_white = r >= 238 and g >= 238 and b >= 238 and max(r, g, b) - min(r, g, b) <= 25
            if near_white:
                pixels[x, y] = (0, 0, 0, 0)

    return rgba


def crop_ground_to_visible_height(image: Image.Image, padding: int = 4) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha_bbox = rgba.getchannel("A").getbbox()
    if alpha_bbox is None:
        return rgba

    _left, top, _right, bottom = alpha_bbox
    top = max(0, top - padding)
    bottom = min(rgba.height, bottom + padding)
    return rgba.crop((0, top, rgba.width, bottom))


def convert_asset(output_name: str, source_name: str) -> None:
    source_path = DOWNLOADS_DIR / source_name
    output_path = ASSET_DIR / output_name

    if not source_path.exists():
        raise FileNotFoundError(f"Imagem de origem nao encontrada: {source_path}")

    with Image.open(source_path) as image:
        if should_make_white_transparent(output_name):
            converted = make_white_transparent(image)
        else:
            converted = image.convert("RGBA")

        if output_name in GROUND_NAMES:
            converted = crop_ground_to_visible_height(converted)

        converted.save(output_path)
        print(f"{source_path.name} -> assets/{output_name}")


def create_flag_image(source_path: Path = FLAG_SOURCE_PATH) -> Image.Image:
    if not source_path.exists():
        raise FileNotFoundError(
            f"Imagem da bandeira nao encontrada: {source_path}\n"
            f"Coloque o arquivo '{FLAG_SOURCE_NAME}' em {DOWNLOADS_DIR}."
        )

    with Image.open(source_path) as image:
        flag = remove_hunter_sheet_background(image)

    alpha_bbox = flag.getchannel("A").getbbox()
    if alpha_bbox is None:
        return flag

    return flag.crop(alpha_bbox)


def create_flag() -> None:
    output_path = ASSET_DIR / "bandeira.png"
    image = create_flag_image()
    image.save(output_path)
    print(f"{FLAG_SOURCE_NAME} -> assets/bandeira.png")


def create_menu_background_image(source_path: Path = MENU_BACKGROUND_SOURCE_PATH) -> Image.Image:
    if not source_path.exists():
        raise FileNotFoundError(
            f"Imagem de fundo do menu nao encontrada: {source_path}\n"
            f"Coloque o arquivo '{MENU_BACKGROUND_SOURCE_NAME}' em {DOWNLOADS_DIR}."
        )

    with Image.open(source_path) as image:
        return image.convert("RGBA")


def remove_menu_button_background(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()

    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = pixels[x, y]
            neutral_light = r >= 218 and g >= 218 and b >= 218 and max(r, g, b) - min(r, g, b) <= 36
            pale_outer_glow = (
                r >= 245
                and g >= 210
                and b >= 205
                and (
                    y <= rgba.height * 0.27
                    or y >= rgba.height * 0.73
                    or x <= rgba.width * 0.12
                    or x >= rgba.width * 0.88
                )
            )
            if neutral_light or pale_outer_glow:
                pixels[x, y] = (0, 0, 0, 0)

    return rgba


def remove_edge_connected_menu_glow(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size

    def is_glow_pixel(x: int, y: int) -> bool:
        r, g, b, a = pixels[x, y]
        if a <= 20:
            return False

        pale_warm = r >= 220 and g >= 130 and b >= 120 and (r - g) <= 125
        bright_red = r >= 190 and (r - g) >= 75 and (r - b) >= 70 and g >= 25 and b >= 25
        return pale_warm or bright_red

    queue = deque()
    visited = set()

    for x in range(width):
        for y in (0, height - 1):
            if is_glow_pixel(x, y):
                visited.add((x, y))
                queue.append((x, y))

    for y in range(height):
        for x in (0, width - 1):
            if (x, y) not in visited and is_glow_pixel(x, y):
                visited.add((x, y))
                queue.append((x, y))

    while queue:
        x, y = queue.popleft()
        pixels[x, y] = (0, 0, 0, 0)

        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited and is_glow_pixel(nx, ny):
                visited.add((nx, ny))
                queue.append((nx, ny))

    return rgba


def remove_small_alpha_components(image: Image.Image, min_pixels: int = 24) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    visited = set()

    for start_y in range(height):
        for start_x in range(width):
            if (start_x, start_y) in visited or pixels[start_x, start_y][3] <= 20:
                continue

            component = []
            queue = deque([(start_x, start_y)])
            visited.add((start_x, start_y))

            while queue:
                x, y = queue.popleft()
                component.append((x, y))

                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        if pixels[nx, ny][3] > 20:
                            queue.append((nx, ny))

            if len(component) < min_pixels:
                for x, y in component:
                    pixels[x, y] = (0, 0, 0, 0)

    return rgba


def create_menu_selected_button_image(source_path: Path = MENU_SELECTED_BUTTON_SOURCE_PATH) -> Image.Image:
    if not source_path.exists():
        raise FileNotFoundError(
            f"Imagem do botao selecionado nao encontrada: {source_path}\n"
            f"Coloque o arquivo '{MENU_SELECTED_BUTTON_SOURCE_NAME}' em {DOWNLOADS_DIR}."
        )

    with Image.open(source_path) as image:
        button = remove_menu_button_background(image)

    alpha_bbox = button.getchannel("A").getbbox()
    if alpha_bbox is None:
        return button

    button = remove_edge_connected_menu_glow(button.crop(alpha_bbox))
    button = remove_small_alpha_components(button)
    alpha_bbox = button.getchannel("A").getbbox()
    if alpha_bbox is None:
        return button

    return button.crop(alpha_bbox)


def create_menu_assets() -> None:
    create_menu_background_image().save(ASSET_DIR / "menu_fundo.png")
    print(f"{MENU_BACKGROUND_SOURCE_NAME} -> assets/menu_fundo.png")

    create_menu_selected_button_image().save(ASSET_DIR / "menu_botao_selecionado.png")
    print(f"{MENU_SELECTED_BUTTON_SOURCE_NAME} -> assets/menu_botao_selecionado.png")


def create_life_icon_image() -> Image.Image:
    image = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.ellipse((22, 22, 66, 68), fill=(145, 18, 35, 255))
    draw.ellipse((62, 22, 106, 68), fill=(145, 18, 35, 255))
    draw.polygon([(18, 49), (110, 49), (64, 112)], fill=(145, 18, 35, 255))

    draw.ellipse((31, 28, 61, 58), fill=(230, 48, 70, 255))
    draw.ellipse((67, 28, 97, 58), fill=(230, 48, 70, 255))
    draw.polygon([(28, 52), (100, 52), (64, 101)], fill=(230, 48, 70, 255))
    draw.ellipse((42, 35, 54, 47), fill=(255, 138, 150, 180))

    return image


def create_life_icon() -> None:
    output_path = ASSET_DIR / "vida.png"
    create_life_icon_image().save(output_path)
    print("vida gerada -> assets/vida.png")


def remove_hunter_sheet_background(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()

    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = pixels[x, y]
            neutral_light = r >= 218 and g >= 218 and b >= 218 and max(r, g, b) - min(r, g, b) <= 32
            if neutral_light:
                pixels[x, y] = (0, 0, 0, 0)

    return rgba


def crop_box_with_margin(image: Image.Image, box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    left, top, right, bottom = box
    return (
        max(0, left - HUNTER_SHEET_CROP_MARGIN),
        max(0, top - HUNTER_SHEET_CROP_MARGIN),
        min(image.width, right + HUNTER_SHEET_CROP_MARGIN),
        min(image.height, bottom + HUNTER_SHEET_CROP_MARGIN),
    )


def create_hunter_sheet_frames(source_path: Path = HUNTER_SHEET_PATH) -> dict[str, Image.Image]:
    if not source_path.exists():
        raise FileNotFoundError(
            f"Sprite sheet do cacador nao encontrada: {source_path}\n"
            f"Coloque o arquivo '{HUNTER_SHEET_SOURCE_NAME}' em {DOWNLOADS_DIR}."
        )

    frames = {}
    with Image.open(source_path) as sheet:
        sheet = sheet.convert("RGBA")
        for output_name, box in HUNTER_SHEET_FRAMES.items():
            frame = sheet.crop(crop_box_with_margin(sheet, box))
            frames[output_name] = remove_hunter_sheet_background(frame)

    return frames


def pad_to_canvas(
    image: Image.Image,
    size: tuple[int, int],
    align_bottom: bool = True,
    align_left: bool = False,
) -> Image.Image:
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    x = 0 if align_left else (size[0] - image.width) // 2
    y = size[1] - image.height if align_bottom else (size[1] - image.height) // 2
    canvas.alpha_composite(image, (x, y))
    return canvas


def create_health_bar_frames(source_path: Path = HEALTH_BAR_SOURCE_PATH) -> dict[str, Image.Image]:
    if not source_path.exists():
        raise FileNotFoundError(
            f"Sprite sheet da barra de vida nao encontrada: {source_path}\n"
            f"Coloque o arquivo '{HEALTH_BAR_SOURCE_NAME}' em {DOWNLOADS_DIR}."
        )

    cropped_frames = {}
    max_width = 0
    max_height = 0
    with Image.open(source_path) as sheet:
        sheet = sheet.convert("RGBA")
        for output_name, box in HEALTH_BAR_SHEET_FRAMES.items():
            frame = sheet.crop(crop_box_with_margin(sheet, box))
            frame = remove_hunter_sheet_background(frame)
            cropped_frames[output_name] = frame
            max_width = max(max_width, frame.width)
            max_height = max(max_height, frame.height)

    return {
        output_name: pad_to_canvas(frame, (max_width, max_height))
        for output_name, frame in cropped_frames.items()
    }


def create_player_attack_sheet_frames(source_path: Path = PLAYER_ATTACK_SHEET_PATH) -> dict[str, Image.Image]:
    if not source_path.exists():
        raise FileNotFoundError(
            f"Sprite sheet de ataque do lobo nao encontrada: {source_path}\n"
            f"Coloque o arquivo '{PLAYER_ATTACK_SHEET_SOURCE_NAME}' em {DOWNLOADS_DIR}."
        )

    cropped_frames = {}
    max_width = 0
    max_height = 0
    with Image.open(source_path) as sheet:
        sheet = sheet.convert("RGBA")
        for output_name, box in PLAYER_ATTACK_SHEET_FRAMES.items():
            frame = sheet.crop(crop_box_with_margin(sheet, box))
            frame = remove_hunter_sheet_background(frame)
            cropped_frames[output_name] = frame
            max_width = max(max_width, frame.width)
            max_height = max(max_height, frame.height)

    return {
        output_name: pad_to_canvas(frame, (max_width, max_height), align_left=True)
        for output_name, frame in cropped_frames.items()
    }


def create_hunter_death_sheet_frames(source_path: Path = HUNTER_DEATH_SHEET_PATH) -> dict[str, Image.Image]:
    if not source_path.exists():
        raise FileNotFoundError(
            f"Sprite sheet de morte do cacador nao encontrada: {source_path}\n"
            f"Coloque o arquivo '{HUNTER_DEATH_SHEET_SOURCE_NAME}' em {DOWNLOADS_DIR}."
        )

    cropped_frames = {}
    max_width = 0
    max_height = 0
    with Image.open(source_path) as sheet:
        sheet = sheet.convert("RGBA")
        for output_name, box in HUNTER_DEATH_SHEET_FRAMES.items():
            frame = sheet.crop(crop_box_with_margin(sheet, box))
            frame = remove_hunter_sheet_background(frame)
            cropped_frames[output_name] = frame
            max_width = max(max_width, frame.width)
            max_height = max(max_height, frame.height)

    return {
        output_name: pad_to_canvas(frame, (max_width, max_height))
        for output_name, frame in cropped_frames.items()
    }


def create_bullet_image() -> Image.Image:
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.ellipse((16, 24, 48, 40), fill=(84, 54, 28, 255))
    draw.ellipse((22, 26, 46, 38), fill=(231, 175, 79, 255))
    draw.polygon([(43, 24), (58, 32), (43, 40)], fill=(245, 213, 111, 255))

    return image


def create_blood_frame_image(frame_index: int) -> Image.Image:
    image = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    sizes = [
        [(52, 56, 76, 79), (38, 70, 54, 84), (78, 68, 94, 84)],
        [(34, 54, 80, 96), (75, 48, 101, 76), (20, 80, 42, 103)],
        [(20, 50, 95, 106), (84, 74, 111, 98), (36, 36, 60, 59)],
    ]
    colors = [(155, 7, 24, 255), (210, 20, 41, 255), (96, 0, 17, 255)]

    for idx, box in enumerate(sizes[min(2, max(0, frame_index))]):
        draw.ellipse(box, fill=colors[idx])

    return image


def create_enemy_assets() -> None:
    for output_name, frame in create_hunter_sheet_frames().items():
        frame.save(ASSET_DIR / output_name)
        print(f"{output_name} recortado -> assets/{output_name}")

    for output_name, frame in create_hunter_death_sheet_frames().items():
        frame.save(ASSET_DIR / output_name)
        print(f"{output_name} recortado -> assets/{output_name}")

    create_bullet_image().save(ASSET_DIR / "bullet.png")
    print("bullet gerado -> assets/bullet.png")


def create_player_attack_assets() -> None:
    for output_name, frame in create_player_attack_sheet_frames().items():
        frame.save(ASSET_DIR / output_name)
        print(f"{output_name} recortado -> assets/{output_name}")


def create_health_bar_assets() -> None:
    for output_name, frame in create_health_bar_frames().items():
        frame.save(ASSET_DIR / output_name)
        print(f"{output_name} recortado -> assets/{output_name}")


def main() -> None:
    ASSET_DIR.mkdir(exist_ok=True)

    for output_name, source_name in SOURCE_ASSETS.items():
        convert_asset(output_name, source_name)

    create_flag()
    create_menu_assets()
    create_life_icon()
    create_health_bar_assets()
    create_player_attack_assets()
    create_enemy_assets()
    print("Assets prontos.")


if __name__ == "__main__":
    main()
