import pygame
import random
import time
from persistence import add_score

pygame.mixer.init()

coin_sound = pygame.mixer.Sound("assets/coin.mp3")
crash_sound = pygame.mixer.Sound("assets/crash.mp3")

coin_sound.set_volume(0.5)
crash_sound.set_volume(0.6)

WIDTH = 600
HEIGHT = 700

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ROAD = (45, 45, 45)
LINE = (230, 230, 230)
RED = (220, 30, 30)
BLUE = (30, 100, 255)
GREEN = (30, 200, 70)
YELLOW = (240, 220, 0)
ORANGE = (255, 140, 0)
PURPLE = (150, 50, 220)
BROWN = (120, 70, 30)
GRAY = (120, 120, 120)
WINDOW = (150, 220, 255)

FONT = pygame.font.SysFont("Arial", 24)

LANES = [120, 220, 320, 420]


def play_coin_sound(settings):
    if settings["sound"]:
        coin_sound.play()


def play_crash_sound(settings):
    if settings["sound"]:
        crash_sound.play()
        pygame.time.delay(250)


def color_from_name(name):
    if name == "red":
        return RED
    if name == "green":
        return GREEN
    if name == "yellow":
        return YELLOW
    return BLUE


class Player:
    def __init__(self, settings):
        self.w = 45
        self.h = 75
        self.x = LANES[1]
        self.y = HEIGHT - 120
        self.color = color_from_name(settings["car_color"])
        self.speed = 7
        self.normal_speed = 7
        self.shield = False

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 80:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < 475:
            self.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)

        pygame.draw.rect(screen, WINDOW, (self.x + 9, self.y + 10, 27, 18), border_radius=5)
        pygame.draw.rect(screen, WINDOW, (self.x + 9, self.y + 38, 27, 18), border_radius=5)

        pygame.draw.circle(screen, BLACK, (self.x + 2, self.y + 18), 7)
        pygame.draw.circle(screen, BLACK, (self.x + self.w - 2, self.y + 18), 7)
        pygame.draw.circle(screen, BLACK, (self.x + 2, self.y + 58), 7)
        pygame.draw.circle(screen, BLACK, (self.x + self.w - 2, self.y + 58), 7)

        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)

        if self.shield:
            pygame.draw.circle(screen, YELLOW, self.rect.center, 52, 3)


class TrafficCar:
    def __init__(self, speed, player_x):
        self.w = 50
        self.h = 80

        safe_lanes = [lane for lane in LANES if abs(lane - player_x) > 80]
        self.x = random.choice(safe_lanes if safe_lanes else LANES)

        self.y = -100
        self.speed = speed
        self.car_type = random.choice(["police", "truck", "sport"])

        if self.car_type == "police":
            self.color = BLACK
        elif self.car_type == "truck":
            self.color = BROWN
        else:
            self.color = random.choice([RED, PURPLE, ORANGE])

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        if self.car_type == "police":
            pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, (self.x + 10, self.y, 30, self.h), border_radius=5)

            pygame.draw.rect(screen, WINDOW, (self.x + 12, self.y + 12, 26, 16), border_radius=4)
            pygame.draw.rect(screen, WINDOW, (self.x + 12, self.y + 45, 26, 16), border_radius=4)

            pygame.draw.rect(screen, RED, (self.x + 12, self.y + 32, 10, 8))
            pygame.draw.rect(screen, BLUE, (self.x + 28, self.y + 32, 10, 8))

        elif self.car_type == "truck":
            pygame.draw.rect(screen, self.color, (self.x, self.y + 22, self.w, 55), border_radius=5)
            pygame.draw.rect(screen, GRAY, (self.x + 5, self.y, self.w - 10, 32), border_radius=5)

            pygame.draw.rect(screen, WINDOW, (self.x + 12, self.y + 7, 26, 14), border_radius=4)

            pygame.draw.line(screen, BLACK, (self.x + 5, self.y + 42), (self.x + self.w - 5, self.y + 42), 2)
            pygame.draw.line(screen, BLACK, (self.x + 5, self.y + 58), (self.x + self.w - 5, self.y + 58), 2)

        else:
            pygame.draw.polygon(screen, self.color, [
                (self.x + 8, self.y),
                (self.x + self.w - 8, self.y),
                (self.x + self.w, self.y + 18),
                (self.x + self.w - 5, self.y + self.h),
                (self.x + 5, self.y + self.h),
                (self.x, self.y + 18)
            ])

            pygame.draw.rect(screen, WINDOW, (self.x + 12, self.y + 12, 26, 16), border_radius=5)
            pygame.draw.rect(screen, WINDOW, (self.x + 12, self.y + 42, 26, 16), border_radius=5)

            pygame.draw.circle(screen, YELLOW, (self.x + 12, self.y + 5), 4)
            pygame.draw.circle(screen, YELLOW, (self.x + self.w - 12, self.y + 5), 4)

        pygame.draw.circle(screen, BLACK, (self.x + 2, self.y + 20), 7)
        pygame.draw.circle(screen, BLACK, (self.x + self.w - 2, self.y + 20), 7)
        pygame.draw.circle(screen, BLACK, (self.x + 2, self.y + 62), 7)
        pygame.draw.circle(screen, BLACK, (self.x + self.w - 2, self.y + 62), 7)

        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)


class Obstacle:
    def __init__(self, kind, speed, player_x):
        self.kind = kind
        self.w = 55
        self.h = 35

        safe_lanes = [lane for lane in LANES if abs(lane - player_x) > 80]
        self.x = random.choice(safe_lanes if safe_lanes else LANES)

        self.y = -60
        self.speed = speed

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        if self.kind == "oil":
            # Oil spill
            pygame.draw.ellipse(screen, (10, 10, 10), self.rect)
            pygame.draw.ellipse(screen, (35, 35, 35), (self.x + 8, self.y + 7, self.w - 16, self.h - 14))
            pygame.draw.circle(screen, (90, 90, 90), (int(self.x + 16), int(self.y + 10)), 4)
            pygame.draw.circle(screen, (70, 70, 70), (int(self.x + 34), int(self.y + 22)), 3)

        elif self.kind == "pothole":
            # Pothole / road hole
            pygame.draw.ellipse(screen, (75, 45, 20), self.rect)
            pygame.draw.ellipse(screen, (25, 15, 8), (self.x + 7, self.y + 5, self.w - 14, self.h - 10))
            pygame.draw.arc(screen, (130, 90, 50), (self.x + 6, self.y + 4, self.w - 15, self.h - 10), 3.14, 6.28, 3)

        else:
            # Barrier
            pygame.draw.rect(screen, (200, 50, 50), self.rect, border_radius=6)
            pygame.draw.line(screen, WHITE, (self.x + 3, self.y + 3), (self.x + self.w - 3, self.y + self.h - 3), 4)
            pygame.draw.line(screen, WHITE, (self.x + self.w - 3, self.y + 3), (self.x + 3, self.y + self.h - 3), 4)
            pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=6)


class Coin:
    def __init__(self, speed):
        self.value = random.choice([1, 2, 5])
        self.x = random.choice(LANES) + 18
        self.y = -30
        self.r = 13
        self.speed = speed

    @property
    def rect(self):
        return pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.r)
        text = FONT.render(str(self.value), True, BLACK)
        screen.blit(text, (self.x - 6, self.y - 13))


class PowerUp:
    def __init__(self, speed):
        self.kind = random.choice(["nitro", "shield", "repair"])
        self.x = random.choice(LANES) + 10
        self.y = -40
        self.size = 35
        self.speed = speed
        self.spawn_time = time.time()
        self.timeout = 7

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def update(self):
        self.y += self.speed

    def expired(self):
        return time.time() - self.spawn_time > self.timeout

    def draw(self, screen):
        if self.kind == "nitro":
            color = ORANGE
            label = "N"
        elif self.kind == "shield":
            color = BLUE
            label = "S"
        else:
            color = GREEN
            label = "R"

        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        text = FONT.render(label, True, WHITE)
        screen.blit(text, (self.x + 9, self.y + 3))


class MovingBarrier:
    def __init__(self, speed):
        self.x = 80
        self.y = -60
        self.w = 95
        self.h = 28
        self.speed = speed
        self.side_speed = 3

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self):
        self.y += self.speed
        self.x += self.side_speed

        if self.x < 80 or self.x > 430:
            self.side_speed *= -1

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect, border_radius=8)
        text = FONT.render("!", True, WHITE)
        screen.blit(text, (self.x + 40, self.y))


class NitroStrip:
    def __init__(self, speed):
        self.x = random.choice(LANES)
        self.y = -50
        self.w = 65
        self.h = 28
        self.speed = speed

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, ORANGE, self.rect, border_radius=8)
        text = FONT.render("BOOST", True, WHITE)
        screen.blit(text, (self.x + 2, self.y + 2))


def draw_road(screen, road_offset):
    screen.fill(GREEN)
    pygame.draw.rect(screen, ROAD, (70, 0, 460, HEIGHT))

    for x in [180, 280, 380]:
        for y in range(-80, HEIGHT, 100):
            pygame.draw.rect(screen, LINE, (x, y + road_offset, 8, 50))


def draw_hud(screen, score, coins, distance, active_power, remaining_time, shield_active, finish_distance):
    remaining_distance = max(0, finish_distance - distance)

    lines = [
        f"Score: {score}",
        f"Coins: {coins}",
        f"Distance: {distance}m",
        f"Remaining: {remaining_distance}m"
    ]

    y = 10
    for line in lines:
        text = FONT.render(line, True, WHITE)
        screen.blit(text, (10, y))
        y += 28

    if active_power == "nitro":
        power_text = f"Power: Nitro {remaining_time:.1f}s"
    elif shield_active:
        power_text = "Power: Shield until hit"
    else:
        power_text = "Power: None"

    text = FONT.render(power_text, True, YELLOW)
    screen.blit(text, (330, 10))


def calculate_score(coins, distance, power_bonus):
    return coins * 10 + distance + power_bonus


def run_game(screen, clock, username, settings):
    player = Player(settings)

    difficulty = settings["difficulty"]

    if difficulty == "easy":
        base_speed = 4
        traffic_spawn = 95
        obstacle_spawn = 115
        finish_distance = 3000

    elif difficulty == "hard":
        base_speed = 7
        traffic_spawn = 55
        obstacle_spawn = 80
        finish_distance = 7000

    else:
        base_speed = 5
        traffic_spawn = 75
        obstacle_spawn = 100
        finish_distance = 5000

    traffic = []
    obstacles = []
    coins = []
    powerups = []
    road_events = []

    coin_count = 0
    distance = 0
    power_bonus = 0
    score = 0

    frame = 0
    road_offset = 0

    active_power = None
    nitro_start = 0
    nitro_duration = 0

    while True:
        clock.tick(60)
        frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", score, distance, coin_count

        keys = pygame.key.get_pressed()
        player.move(keys)

        progress_level = distance // 600
        current_speed = base_speed + progress_level * 0.4

        if active_power == "nitro":
            current_speed += 3

            if time.time() - nitro_start >= nitro_duration:
                active_power = None
                nitro_duration = 0

        road_offset = (road_offset + current_speed) % 100
        distance += int(current_speed / 2)

        score = calculate_score(coin_count, distance, power_bonus)

        dynamic_traffic_spawn = max(25, int(traffic_spawn - progress_level * 5))
        dynamic_obstacle_spawn = max(35, int(obstacle_spawn - progress_level * 6))

        if frame % dynamic_traffic_spawn == 0:
            traffic.append(TrafficCar(current_speed + 2, player.x))

        if frame % dynamic_obstacle_spawn == 0:
            kind = random.choice(["oil", "pothole", "barrier"])
            obstacles.append(Obstacle(kind, current_speed, player.x))

        if frame % 80 == 0:
            coins.append(Coin(current_speed))

        if frame % 300 == 0:
            powerups.append(PowerUp(current_speed))

        if frame % 420 == 0:
            event_type = random.choice(["moving_barrier", "nitro_strip"])

            if event_type == "moving_barrier":
                road_events.append(MovingBarrier(current_speed))
            else:
                road_events.append(NitroStrip(current_speed))

        draw_road(screen, road_offset)

        for car in traffic[:]:
            car.update()
            car.draw(screen)

            if car.y > HEIGHT:
                traffic.remove(car)

            elif player.rect.colliderect(car.rect):
                if player.shield:
                    player.shield = False
                    active_power = None
                    traffic.remove(car)
                else:
                    play_crash_sound(settings)
                    add_score(username, score, distance, coin_count)
                    return "game_over", score, distance, coin_count

        for obs in obstacles[:]:
            obs.update()
            obs.draw(screen)

            if obs.y > HEIGHT:
                obstacles.remove(obs)

            elif player.rect.colliderect(obs.rect):
                if player.shield:
                    player.shield = False
                    active_power = None
                    obstacles.remove(obs)

                elif obs.kind == "oil":
                    player.speed = 4
                    obstacles.remove(obs)

                elif obs.kind == "pothole":
                    play_crash_sound(settings)
                    add_score(username, score, distance, coin_count)
                    return "game_over", score, distance, coin_count

                elif obs.kind == "barrier":
                    play_crash_sound(settings)
                    add_score(username, score, distance, coin_count)
                    return "game_over", score, distance, coin_count

        if frame % 120 == 0:
            player.speed = player.normal_speed

        for coin in coins[:]:
            coin.update()
            coin.draw(screen)

            if coin.y > HEIGHT:
                coins.remove(coin)

            elif player.rect.colliderect(coin.rect):
                coin_count += coin.value
                play_coin_sound(settings)
                coins.remove(coin)

        for power in powerups[:]:
            power.update()
            power.draw(screen)

            if power.y > HEIGHT or power.expired():
                powerups.remove(power)

            elif player.rect.colliderect(power.rect):
                if power.kind == "repair":
                    if obstacles:
                        obstacles.pop(0)
                    power_bonus += 150
                    powerups.remove(power)

                elif active_power is None and not player.shield:
                    if power.kind == "nitro":
                        active_power = "nitro"
                        nitro_start = time.time()
                        nitro_duration = 4
                        power_bonus += 100

                    elif power.kind == "shield":
                        active_power = "shield"
                        player.shield = True
                        power_bonus += 100

                    powerups.remove(power)

        for road_event in road_events[:]:
            road_event.update()
            road_event.draw(screen)

            if road_event.y > HEIGHT:
                road_events.remove(road_event)

            elif player.rect.colliderect(road_event.rect):
                if isinstance(road_event, MovingBarrier):
                    if player.shield:
                        player.shield = False
                        active_power = None
                        road_events.remove(road_event)
                    else:
                        play_crash_sound(settings)
                        add_score(username, score, distance, coin_count)
                        return "game_over", score, distance, coin_count

                elif isinstance(road_event, NitroStrip):
                    if active_power is None and not player.shield:
                        active_power = "nitro"
                        nitro_start = time.time()
                        nitro_duration = 4
                        power_bonus += 100

                    road_events.remove(road_event)

        player.draw(screen)

        remaining_time = 0
        if active_power == "nitro":
            remaining_time = max(0, nitro_duration - (time.time() - nitro_start))

        draw_hud(
            screen,
            score,
            coin_count,
            distance,
            active_power,
            remaining_time,
            player.shield,
            finish_distance
        )

        if distance >= finish_distance:
            score += 1000
            add_score(username, score, distance, coin_count)
            return "win", score, distance, coin_count

        pygame.display.update()