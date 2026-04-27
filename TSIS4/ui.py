import pygame
from persistence import load_leaderboard, save_settings

pygame.font.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
LIGHT_GRAY = (160, 160, 160)
GREEN = (0, 180, 0)
RED = (200, 0, 0)
YELLOW = (230, 200, 0)

FONT = pygame.font.SysFont("Arial", 28)
BIG_FONT = pygame.font.SysFont("Arial", 48)


class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)

        text = FONT.render(self.text, True, WHITE)
        screen.blit(
            text,
            (
                self.rect.centerx - text.get_width() // 2,
                self.rect.centery - text.get_height() // 2
            )
        )

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


def draw_text(screen, text, size, color, x, y, center=True):
    font = pygame.font.SysFont("Arial", size)
    img = font.render(text, True, color)

    if center:
        rect = img.get_rect(center=(x, y))
        screen.blit(img, rect)
    else:
        screen.blit(img, (x, y))


def username_screen(screen, clock):
    name = ""

    while True:
        screen.fill(BLACK)

        draw_text(screen, "Enter your name", 42, WHITE, 300, 180)
        draw_text(screen, name + "|", 36, YELLOW, 300, 250)
        draw_text(screen, "Press ENTER to start", 24, LIGHT_GRAY, 300, 330)

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name.strip() == "":
                        name = "Player"
                    return name

                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]

                else:
                    if len(name) < 12:
                        name += event.unicode


def main_menu(screen, clock):
    buttons = {
        "play": Button("Play", 200, 180, 200, 50),
        "leaderboard": Button("Leaderboard", 200, 250, 200, 50),
        "settings": Button("Settings", 200, 320, 200, 50),
        "quit": Button("Quit", 200, 390, 200, 50)
    }

    while True:
        screen.fill(BLACK)
        draw_text(screen, "TSIS3 RACER", 52, YELLOW, 300, 100)

        for button in buttons.values():
            button.draw(screen)

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            for key, button in buttons.items():
                if button.clicked(event):
                    return key


def leaderboard_screen(screen, clock):
    back = Button("Back", 220, 520, 160, 45)

    while True:
        screen.fill(BLACK)
        draw_text(screen, "TOP 10 LEADERBOARD", 40, YELLOW, 300, 60)

        data = load_leaderboard()

        y = 120
        if not data:
            draw_text(screen, "No scores yet", 30, WHITE, 300, 250)
        else:
            for i, item in enumerate(data):
                line = f"{i + 1}. {item['name']} | Score: {item['score']} | Distance: {item['distance']}m"
                draw_text(screen, line, 22, WHITE, 300, y)
                y += 38

        back.draw(screen)

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if back.clicked(event):
                return "menu"


def settings_screen(screen, clock, settings):
    sound_btn = Button("Sound: ON", 190, 160, 220, 50)
    color_btn = Button("Car Color", 190, 230, 220, 50)
    diff_btn = Button("Difficulty", 190, 300, 220, 50)
    back_btn = Button("Back", 190, 430, 220, 50)

    colors = ["blue", "red", "green", "yellow"]
    difficulties = ["easy", "normal", "hard"]

    while True:
        screen.fill(BLACK)

        draw_text(screen, "SETTINGS", 46, YELLOW, 300, 80)

        sound_btn.text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
        color_btn.text = f"Color: {settings['car_color']}"
        diff_btn.text = f"Difficulty: {settings['difficulty']}"

        sound_btn.draw(screen)
        color_btn.draw(screen)
        diff_btn.draw(screen)
        back_btn.draw(screen)

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(settings)
                return "quit"

            if sound_btn.clicked(event):
                settings["sound"] = not settings["sound"]
                save_settings(settings)

            if color_btn.clicked(event):
                index = colors.index(settings["car_color"])
                settings["car_color"] = colors[(index + 1) % len(colors)]
                save_settings(settings)

            if diff_btn.clicked(event):
                index = difficulties.index(settings["difficulty"])
                settings["difficulty"] = difficulties[(index + 1) % len(difficulties)]
                save_settings(settings)

            if back_btn.clicked(event):
                save_settings(settings)
                return "menu"


def game_over_screen(screen, clock, score, distance, coins, win=False):
    retry = Button("Retry", 190, 330, 220, 50)
    menu = Button("Main Menu", 190, 400, 220, 50)

    while True:
        screen.fill(BLACK)

        if win:
            draw_text(screen, "YOU WIN!", 52, GREEN, 300, 120)
            draw_text(screen, "Finish distance reached!", 26, YELLOW, 300, 165)
        else:
            draw_text(screen, "GAME OVER", 52, RED, 300, 120)

        draw_text(screen, f"Score: {score}", 30, WHITE, 300, 210)
        draw_text(screen, f"Distance: {distance}m", 30, WHITE, 300, 250)
        draw_text(screen, f"Coins: {coins}", 30, WHITE, 300, 290)

        retry.draw(screen)
        menu.draw(screen)

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if retry.clicked(event):
                return "retry"

            if menu.clicked(event):
                return "menu"
