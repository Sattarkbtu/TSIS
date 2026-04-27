import pygame
from ui import (
    main_menu,
    leaderboard_screen,
    settings_screen,
    game_over_screen,
    username_screen
)
from racer import run_game
from persistence import load_settings

pygame.init()
pygame.mixer.init()

WIDTH = 600
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS3 Racer Game")

clock = pygame.time.Clock()


def start_music(settings):
    try:
        if settings["sound"]:
            pygame.mixer.music.load("assets/soundtrack.mp3")
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
    except:
        pass


def stop_music():
    pygame.mixer.music.stop()


def main():
    settings = load_settings()

    while True:
        action = main_menu(screen, clock)

        if action == "quit":
            break

        elif action == "play":
            username = username_screen(screen, clock)

            if username is None:
                break

            while True:
                # 🔥 Музыка тек ойын басталғанда қосылады
                start_music(settings)

                result, score, distance, coins = run_game(screen, clock, username, settings)

                # 🔥 Ойын біткенде музыка өшеді
                stop_music()

                if result == "quit":
                    pygame.quit()
                    return

                over_action = game_over_screen(
                    screen,
                    clock,
                    score,
                    distance,
                    coins,
                    win=(result == "win")
                )

                if over_action == "retry":
                    continue

                elif over_action == "menu":
                    break

                elif over_action == "quit":
                    pygame.quit()
                    return

        elif action == "leaderboard":
            result = leaderboard_screen(screen, clock)
            if result == "quit":
                break

        elif action == "settings":
            result = settings_screen(screen, clock, settings)

            if result == "quit":
                break

    stop_music()
    pygame.quit()


if __name__ == "__main__":
    main()