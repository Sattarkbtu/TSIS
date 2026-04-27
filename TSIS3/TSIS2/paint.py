import pygame
import sys
from datetime import datetime
from tools import flood_fill, draw_shape

pygame.init()

WIDTH, HEIGHT = 1000, 700
TOOLBAR_HEIGHT = 90

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS2 Paint Application")

font = pygame.font.SysFont("Arial", 18)
text_font = pygame.font.SysFont("Arial", 32)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (210, 210, 210)
DARK_GRAY = (120, 120, 120)
RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 220, 0)
PURPLE = (150, 0, 200)
ORANGE = (255, 140, 0)

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

current_color = BLACK
brush_size = 5
current_tool = "pencil"

drawing = False
start_pos = None
last_pos = None

text_mode = False
text_pos = None
text_value = ""

tools = [
    ("pencil", "Pencil"),
    ("line", "Line"),
    ("rectangle", "Rect"),
    ("circle", "Circle"),
    ("eraser", "Eraser"),
    ("fill", "Fill"),
    ("text", "Text"),
    ("square", "Square"),
    ("right_triangle", "R-Tri"),
    ("equilateral_triangle", "E-Tri"),
    ("rhombus", "Rhombus")
]

colors = [
    (BLACK, "Black"),
    (RED, "Red"),
    (GREEN, "Green"),
    (BLUE, "Blue"),
    (YELLOW, "Yellow"),
    (PURPLE, "Purple"),
    (ORANGE, "Orange")
]


def canvas_pos(pos):
    return pos[0], pos[1] - TOOLBAR_HEIGHT


def inside_canvas(pos):
    return pos[1] >= TOOLBAR_HEIGHT


def draw_button(rect, text, active=False):
    color = DARK_GRAY if active else GRAY
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    label = font.render(text, True, BLACK)
    screen.blit(label, (rect.x + 5, rect.y + 8))


def draw_toolbar():
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))

    x = 5
    y = 5

    for tool_key, tool_name in tools:
        rect = pygame.Rect(x, y, 80, 35)
        draw_button(rect, tool_name, current_tool == tool_key)
        x += 85

    x = 5
    y = 50

    for color, name in colors:
        rect = pygame.Rect(x, y, 35, 30)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 3 if current_color == color else 1)
        x += 42

    info = f"Brush: {brush_size}px | 1/2/3 Size | C=Clear | Ctrl+S=Save"
    size_text = font.render(info, True, BLACK)
    screen.blit(size_text, (340, 55))


def get_clicked_tool(pos):
    x = 5
    y = 5

    for tool_key, tool_name in tools:
        rect = pygame.Rect(x, y, 80, 35)
        if rect.collidepoint(pos):
            return tool_key
        x += 85

    return None


def get_clicked_color(pos):
    x = 5
    y = 50

    for color, name in colors:
        rect = pygame.Rect(x, y, 35, 30)
        if rect.collidepoint(pos):
            return color
        x += 42

    return None


def save_canvas():
    filename = "paint_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
    pygame.image.save(canvas, filename)
    print(f"Saved: {filename}")


def clear_canvas():
    canvas.fill(WHITE)
    print("Canvas cleared")


running = True

while running:
    mouse_pos = pygame.mouse.get_pos()

    screen.fill(WHITE)
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))
    draw_toolbar()

    preview_surface = canvas.copy()

    if drawing and start_pos and inside_canvas(mouse_pos):
        end_pos = canvas_pos(mouse_pos)

        if current_tool in [
            "line",
            "rectangle",
            "circle",
            "square",
            "right_triangle",
            "equilateral_triangle",
            "rhombus"
        ]:
            draw_shape(preview_surface, current_tool, start_pos, end_pos, current_color, brush_size)
            screen.blit(preview_surface, (0, TOOLBAR_HEIGHT))
            draw_toolbar()

    if text_mode and text_pos:
        display_text = text_font.render(text_value + "|", True, current_color)
        screen.blit(display_text, (text_pos[0], text_pos[1] + TOOLBAR_HEIGHT))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                if event.key == pygame.K_s:
                    save_canvas()

            if event.key == pygame.K_c:
                clear_canvas()

            if event.key == pygame.K_1:
                brush_size = 2
            elif event.key == pygame.K_2:
                brush_size = 5
            elif event.key == pygame.K_3:
                brush_size = 10

            if text_mode:
                if event.key == pygame.K_RETURN:
                    final_text = text_font.render(text_value, True, current_color)
                    canvas.blit(final_text, text_pos)
                    text_mode = False
                    text_value = ""
                    text_pos = None

                elif event.key == pygame.K_ESCAPE:
                    text_mode = False
                    text_value = ""
                    text_pos = None

                elif event.key == pygame.K_BACKSPACE:
                    text_value = text_value[:-1]

                else:
                    if event.unicode:
                        text_value += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            clicked_tool = get_clicked_tool(pos)
            clicked_color = get_clicked_color(pos)

            if clicked_tool:
                current_tool = clicked_tool
                continue

            if clicked_color:
                current_color = clicked_color
                continue

            if inside_canvas(pos):
                cpos = canvas_pos(pos)

                if current_tool == "fill":
                    flood_fill(canvas, cpos, current_color)

                elif current_tool == "text":
                    text_mode = True
                    text_pos = cpos
                    text_value = ""

                else:
                    drawing = True
                    start_pos = cpos
                    last_pos = cpos

        if event.type == pygame.MOUSEMOTION:
            if drawing and inside_canvas(event.pos):
                cpos = canvas_pos(event.pos)

                if current_tool == "pencil":
                    pygame.draw.line(canvas, current_color, last_pos, cpos, brush_size)
                    last_pos = cpos

                elif current_tool == "eraser":
                    pygame.draw.line(canvas, WHITE, last_pos, cpos, brush_size)
                    last_pos = cpos

        if event.type == pygame.MOUSEBUTTONUP:
            if drawing and inside_canvas(event.pos):
                end_pos = canvas_pos(event.pos)

                if current_tool in [
                    "line",
                    "rectangle",
                    "circle",
                    "square",
                    "right_triangle",
                    "equilateral_triangle",
                    "rhombus"
                ]:
                    draw_shape(canvas, current_tool, start_pos, end_pos, current_color, brush_size)

            drawing = False
            start_pos = None
            last_pos = None

pygame.quit()
sys.exit()
