from dataclasses import dataclass, field
import math
import random


GROUND_Y = -0.93
SPAWN_INTERVAL = 6.0
MIN_SPAWN_INTERVAL = 2.7
HUNTER_SPAWN_AHEAD = 1.25
HUNTER_SPAWN_RANDOM_AHEAD = 0.35
MAX_HUNTER_SPAWN_RANDOM_AHEAD = 1.2
MAX_HUNTERS = 3
MAX_HUNTERS_LIMIT = 6
HUNTER_Y = GROUND_Y
HUNTER_W = 0.30
HUNTER_H = 0.40
HUNTER_KILL_DISTANCE = 0.34
HUNTER_SHOOT_INTERVAL = 1.4
MIN_HUNTER_SHOOT_INTERVAL = 0.8
HUNTER_SHOOT_FLASH = 0.2
HUNTER_SPEED_STEP = 0.05
HUNTER_TYPE_GUNNER = "hunter"
HUNTER_TYPE_SCOUT = "scout"
HUNTER_TYPE_BRUTE = "brute"
ENEMY_TYPES = (HUNTER_TYPE_GUNNER, HUNTER_TYPE_SCOUT, HUNTER_TYPE_BRUTE)

BULLET_SPEED = 0.85
BULLET_SPEED_STEP = 0.18
MAX_BULLET_SPEED = 1.55
BULLET_MAX_AGE = 4.0
BULLET_RADIUS = 0.025

BLOOD_FRAME_TIME = 0.12
BLOOD_TOTAL_TIME = BLOOD_FRAME_TIME * 3

INVULNERAVEL_DURACAO = 1.0
PHASE_LENGTH = 5.0
MAX_HUNTER_SPEED = 0.25

# Hitbox local do player na tela/mundo: x1, y1, x2, y2.
PLAYER_HITBOX = (0.12, -0.83, 0.38, -0.51)


@dataclass
class Hunter:
    x: float
    y: float = HUNTER_Y
    shoot_timer: float = 0.0
    shoot_flash: float = 0.0
    enemy_type: str = HUNTER_TYPE_GUNNER


@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float
    age: float = 0.0


@dataclass
class BloodEffect:
    x: float
    y: float
    age: float = 0.0


@dataclass(frozen=True)
class Difficulty:
    level: int
    spawn_interval: float
    max_hunters: int
    shoot_interval: float
    bullet_speed: float
    hunter_speed: float
    spawn_jitter: float


@dataclass(frozen=True)
class EnemyTypeSpec:
    unlock_level: int
    spawn_weight: int
    shoot_interval_multiplier: float
    bullet_speed_multiplier: float
    move_speed_multiplier: float
    move_speed_bonus: float


ENEMY_TYPE_SPECS = {
    HUNTER_TYPE_GUNNER: EnemyTypeSpec(
        unlock_level=1,
        spawn_weight=5,
        shoot_interval_multiplier=1.0,
        bullet_speed_multiplier=1.0,
        move_speed_multiplier=1.0,
        move_speed_bonus=0.0,
    ),
    HUNTER_TYPE_SCOUT: EnemyTypeSpec(
        unlock_level=2,
        spawn_weight=3,
        shoot_interval_multiplier=1.15,
        bullet_speed_multiplier=0.9,
        move_speed_multiplier=1.8,
        move_speed_bonus=0.10,
    ),
    HUNTER_TYPE_BRUTE: EnemyTypeSpec(
        unlock_level=3,
        spawn_weight=2,
        shoot_interval_multiplier=1.45,
        bullet_speed_multiplier=1.25,
        move_speed_multiplier=0.65,
        move_speed_bonus=0.02,
    ),
}


@dataclass
class GameState:
    hunters: list[Hunter] = field(default_factory=list)
    bullets: list[Bullet] = field(default_factory=list)
    blood_effects: list[BloodEffect] = field(default_factory=list)
    spawn_timer: float = 0.0
    vidas: int = 3
    invulneravel_timer: float = 0.0
    nivel: int = 1


def center_of_box(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def offset_box(box, dx, dy=0.0):
    x1, y1, x2, y2 = box
    return (x1 + dx, y1 + dy, x2 + dx, y2 + dy)


def hunter_center(hunter):
    return (hunter.x + HUNTER_W / 2, hunter.y + HUNTER_H / 2)


def normalize(dx, dy):
    length = math.hypot(dx, dy)
    if length == 0:
        return (-1.0, 0.0)
    return (dx / length, dy / length)


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def difficulty_level_for_progress(progress_x):
    progress = max(0.0, progress_x)
    return int(progress // PHASE_LENGTH) + 1


def difficulty_for_level(level):
    safe_level = max(1, int(level))
    extra = safe_level - 1
    return Difficulty(
        level=safe_level,
        spawn_interval=max(MIN_SPAWN_INTERVAL, SPAWN_INTERVAL - 0.9 * extra),
        max_hunters=min(MAX_HUNTERS_LIMIT, MAX_HUNTERS + extra),
        shoot_interval=max(MIN_HUNTER_SHOOT_INTERVAL, HUNTER_SHOOT_INTERVAL - 0.2 * extra),
        bullet_speed=min(MAX_BULLET_SPEED, BULLET_SPEED + BULLET_SPEED_STEP * extra),
        hunter_speed=min(MAX_HUNTER_SPEED, HUNTER_SPEED_STEP * extra),
        spawn_jitter=min(MAX_HUNTER_SPAWN_RANDOM_AHEAD, HUNTER_SPAWN_RANDOM_AHEAD * extra),
    )


def difficulty_for_progress(progress_x):
    return difficulty_for_level(difficulty_level_for_progress(progress_x))


def enemy_type_spec(enemy_type):
    return ENEMY_TYPE_SPECS.get(enemy_type, ENEMY_TYPE_SPECS[HUNTER_TYPE_GUNNER])


def enemy_types_for_level(level):
    safe_level = max(1, int(level))
    return tuple(
        enemy_type
        for enemy_type in ENEMY_TYPES
        if safe_level >= enemy_type_spec(enemy_type).unlock_level
    )


def choose_enemy_type(level):
    available_types = enemy_types_for_level(level)
    weights = [enemy_type_spec(enemy_type).spawn_weight for enemy_type in available_types]
    return random.choices(available_types, weights=weights, k=1)[0]


def spawn_hunter(state, camera_x, difficulty=None, enemy_type=None):
    difficulty = difficulty or difficulty_for_level(state.nivel)
    random_ahead = random.uniform(0.0, difficulty.spawn_jitter) if difficulty.spawn_jitter > 0 else 0.0
    state.hunters.append(
        Hunter(
            x=camera_x + HUNTER_SPAWN_AHEAD + random_ahead,
            enemy_type=enemy_type or choose_enemy_type(difficulty.level),
        )
    )


def create_bullet_from_hunter(hunter, player_center, bullet_speed=BULLET_SPEED):
    origin_x, origin_y = hunter_center(hunter)
    direction_x, direction_y = normalize(player_center[0] - origin_x, player_center[1] - origin_y)
    return Bullet(
        x=origin_x,
        y=origin_y,
        vx=direction_x * bullet_speed,
        vy=direction_y * bullet_speed,
    )


def move_hunter_toward_player(hunter, dt, player_center, speed):
    if speed <= 0.0:
        return

    direction = 1.0 if player_center[0] > hunter_center(hunter)[0] else -1.0
    hunter.x += direction * speed * dt


def update_hunters_and_spawns(state, dt, camera_x, player_center, progress_x=0.0, level=None):
    difficulty = difficulty_for_level(level) if level is not None else difficulty_for_progress(progress_x)
    state.nivel = difficulty.level
    state.spawn_timer += dt

    while state.spawn_timer >= difficulty.spawn_interval and len(state.hunters) < difficulty.max_hunters:
        state.spawn_timer -= difficulty.spawn_interval
        spawn_hunter(state, camera_x, difficulty)

    for hunter in state.hunters:
        spec = enemy_type_spec(hunter.enemy_type)
        hunter_speed = difficulty.hunter_speed * spec.move_speed_multiplier + spec.move_speed_bonus
        shoot_interval = max(MIN_HUNTER_SHOOT_INTERVAL, difficulty.shoot_interval * spec.shoot_interval_multiplier)
        bullet_speed = min(MAX_BULLET_SPEED, difficulty.bullet_speed * spec.bullet_speed_multiplier)

        move_hunter_toward_player(hunter, dt, player_center, hunter_speed)
        hunter.shoot_timer += dt
        hunter.shoot_flash = max(0.0, hunter.shoot_flash - dt)
        if hunter.shoot_timer >= shoot_interval:
            hunter.shoot_timer -= shoot_interval
            hunter.shoot_flash = HUNTER_SHOOT_FLASH
            state.bullets.append(create_bullet_from_hunter(hunter, player_center, bullet_speed))


def point_hits_box(x, y, box, radius=0.0):
    x1, y1, x2, y2 = box
    return (x1 - radius) <= x <= (x2 + radius) and (y1 - radius) <= y <= (y2 + radius)


def update_bullets_and_damage(state, dt, player_box):
    state.invulneravel_timer = max(0.0, state.invulneravel_timer - dt)
    remaining = []

    for bullet in state.bullets:
        bullet.x += bullet.vx * dt
        bullet.y += bullet.vy * dt
        bullet.age += dt

        hit_player = point_hits_box(bullet.x, bullet.y, player_box, BULLET_RADIUS)
        expired = bullet.age >= BULLET_MAX_AGE or abs(bullet.x) > 50 or abs(bullet.y) > 5

        if hit_player:
            if state.invulneravel_timer <= 0.0 and state.vidas > 0:
                state.vidas -= 1
                state.invulneravel_timer = INVULNERAVEL_DURACAO
            continue

        if not expired:
            remaining.append(bullet)

    state.bullets = remaining


def update_player_hunter_combat(state, player_box):
    player_center = center_of_box(player_box)
    surviving_hunters = []

    for hunter in state.hunters:
        hx, hy = hunter_center(hunter)
        distance = math.hypot(player_center[0] - hx, player_center[1] - hy)
        if distance <= HUNTER_KILL_DISTANCE:
            state.blood_effects.append(BloodEffect(x=hunter.x, y=hunter.y))
        else:
            surviving_hunters.append(hunter)

    state.hunters = surviving_hunters


def update_blood_effects(state, dt):
    remaining = []
    for effect in state.blood_effects:
        effect.age += dt
        if effect.age < BLOOD_TOTAL_TIME:
            remaining.append(effect)
    state.blood_effects = remaining


def blood_frame_index(effect):
    return min(2, int(effect.age / BLOOD_FRAME_TIME))
