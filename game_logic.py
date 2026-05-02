from dataclasses import dataclass, field
import math


GROUND_Y = -0.93
SPAWN_INTERVAL = 6.0
HUNTER_SPAWN_AHEAD = 1.25
MAX_HUNTERS = 3
HUNTER_Y = GROUND_Y
HUNTER_W = 0.30
HUNTER_H = 0.40
HUNTER_KILL_DISTANCE = 0.34
HUNTER_SHOOT_INTERVAL = 1.4
HUNTER_SHOOT_FLASH = 0.2

BULLET_SPEED = 0.85
BULLET_MAX_AGE = 4.0
BULLET_RADIUS = 0.025

BLOOD_FRAME_TIME = 0.12
BLOOD_TOTAL_TIME = BLOOD_FRAME_TIME * 3

INVULNERAVEL_DURACAO = 1.0

# Hitbox local do player na tela/mundo: x1, y1, x2, y2.
PLAYER_HITBOX = (0.12, -0.83, 0.38, -0.51)


@dataclass
class Hunter:
    x: float
    y: float = HUNTER_Y
    shoot_timer: float = 0.0
    shoot_flash: float = 0.0


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


@dataclass
class GameState:
    hunters: list[Hunter] = field(default_factory=list)
    bullets: list[Bullet] = field(default_factory=list)
    blood_effects: list[BloodEffect] = field(default_factory=list)
    spawn_timer: float = 0.0
    vidas: int = 3
    invulneravel_timer: float = 0.0


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


def spawn_hunter(state, camera_x):
    state.hunters.append(Hunter(x=camera_x + HUNTER_SPAWN_AHEAD))


def create_bullet_from_hunter(hunter, player_center):
    origin_x, origin_y = hunter_center(hunter)
    direction_x, direction_y = normalize(player_center[0] - origin_x, player_center[1] - origin_y)
    return Bullet(
        x=origin_x,
        y=origin_y,
        vx=direction_x * BULLET_SPEED,
        vy=direction_y * BULLET_SPEED,
    )


def update_hunters_and_spawns(state, dt, camera_x, player_center):
    state.spawn_timer += dt
    if state.spawn_timer >= SPAWN_INTERVAL and len(state.hunters) < MAX_HUNTERS:
        state.spawn_timer -= SPAWN_INTERVAL
        spawn_hunter(state, camera_x)

    for hunter in state.hunters:
        hunter.shoot_timer += dt
        hunter.shoot_flash = max(0.0, hunter.shoot_flash - dt)
        if hunter.shoot_timer >= HUNTER_SHOOT_INTERVAL:
            hunter.shoot_timer -= HUNTER_SHOOT_INTERVAL
            hunter.shoot_flash = HUNTER_SHOOT_FLASH
            state.bullets.append(create_bullet_from_hunter(hunter, player_center))


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
