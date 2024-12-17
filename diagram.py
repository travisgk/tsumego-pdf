import json
import os
import random
from PIL import Image, ImageDraw, ImageFont


DPI = 300

PROBLEMS = None
def load_problems():
    global PROBLEMS
    if PROBLEMS is not None:
        return

    local_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(local_dir, "chikun-problems.json")
  
    with open(file_path, "r") as file:
        PROBLEMS = json.load(file)

def draw_board(width_in):
    LINE_WIDTH_IN = 1/128
    LINE_COLOR = (128, 128, 128)
    STAR_POINT_RADIUS_IN = 1/96
    width, height = round(width_in * DPI), round(width_in * DPI)
    image = Image.new("RGB", (width, height), "white")

    # Create a drawing object
    draw = ImageDraw.Draw(image)

    # Draw a line
    start_point = (50, 50)  # Starting coordinates (x, y)
    end_point = (350, 350)  # Ending coordinates (x, y)
    line_width = max(1, round(LINE_WIDTH_IN * DPI))

    cell_size_px = width_in/19 * DPI

    for x in range(19):
        draw_x = round(cell_size_px/2 + x*cell_size_px)
        y0 = round(cell_size_px/2)
        y1 = round(y0 + 18*cell_size_px)
        draw.line([(draw_x, y0 - line_width//2 + 1), (draw_x, y1 + line_width//2 - 1)], fill=LINE_COLOR, width=line_width)

    for y in range(19):
        draw_y = round(cell_size_px/2 + y*cell_size_px)
        x0 = round(cell_size_px/2)
        x1 = round(x0 + 18*cell_size_px)
        draw.line([(x0 - line_width//2 + 1, draw_y), (x1 + line_width//2 - 1, draw_y)], fill=LINE_COLOR, width=line_width)

    radius_px = round(STAR_POINT_RADIUS_IN * DPI)
    STAR_POINTS = [(3, 3), (3, 9), (9, 3), (15, 15), (3, 15), (15, 3), (9, 9), (15, 9), (9, 15)]
    for p in STAR_POINTS:
        x = round(cell_size_px/2 + p[0]*cell_size_px)
        y = round(cell_size_px/2 + p[1]*cell_size_px)
        bbox = (x - radius_px, y - radius_px, x + radius_px + radius_px%2, y + radius_px + radius_px%2)
        draw.ellipse(bbox, fill=LINE_COLOR)

    return image, draw

_FONT = None
_LAST_STONE_SIZE = None
_BLACK_STONE_IMAGE = None
_WHITE_STONE_IMAGE = None
GRAPHIC_PADDING_PX = 6

def create_stone_graphic(stone_size_px, is_black: bool):
    OUTLINE_THICKNESS_IN = 1/128
    scale = 4
    w = stone_size_px + GRAPHIC_PADDING_PX * 2
    h = stone_size_px + GRAPHIC_PADDING_PX * 2
    large_size = (round(w * scale), round(h * scale))
    large_image = Image.new("RGBA", large_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(large_image)
    
    center = (large_size[0] / 2, large_size[1] / 2)

    outer_radius = int(stone_size_px/2 * 4)

    fill_color = "black"
    bbox = (
        center[0] - outer_radius,
        center[1] - outer_radius,
        center[0] + outer_radius,
        center[1] + outer_radius,
    )
    draw.ellipse(bbox, fill=fill_color)

    if not is_black:
        
        inner_radius = round(outer_radius - OUTLINE_THICKNESS_IN * 4 * DPI)
        fill_color = "white"
        
        bbox = (
            center[0] - inner_radius,
            center[1] - inner_radius,
            center[0] + inner_radius,
            center[1] + inner_radius,
        )
        draw.ellipse(bbox, fill=fill_color)

    return large_image.resize(
        (int(w) + int(w)%2, int(h) + int(h)%2),
        Image.Resampling.LANCZOS,
    )


def draw_stone(board, x, y, stone_size_px, is_black: bool):
    global _LAST_STONE_SIZE, _BLACK_STONE_IMAGE, _WHITE_STONE_IMAGE
    if _LAST_STONE_SIZE != stone_size_px:
        _BLACK_STONE_IMAGE = create_stone_graphic(stone_size_px, is_black=True)
        _WHITE_STONE_IMAGE = create_stone_graphic(stone_size_px, is_black=False)
        _LAST_STONE_SIZE = stone_size_px

    draw_x = round(x * stone_size_px) - GRAPHIC_PADDING_PX
    draw_y = round(y * stone_size_px) - GRAPHIC_PADDING_PX
    img = _BLACK_STONE_IMAGE if is_black else _WHITE_STONE_IMAGE
    board.paste(img, (draw_x, draw_y), mask=img)
    
        
def make_diagram(
    category: str,
    problem_num: int,
    board_graphic_width_in,
    random_flip: bool=False
):
    CELLS_WIDE = 12
    load_problems()

    flip_xy = random.choice([True, False]) if random_flip else False
    flip_x = random.choice([True, False]) if random_flip else False
    flip_y = random.choice([True, False]) if random_flip else False

    board, board_draw = draw_board(width_in=board_graphic_width_in)
    stone_size_px = (board_graphic_width_in/19 * DPI)

    category = category.lower()
    lines = PROBLEMS.get(category)
    if lines is None:
        print(f"'{category}'' is not a category in Cho Chikun's Life-and-Death problems.")
        print("\t- Elementary\n\t- Intermediate\n\t- Advanced")
        return None

    lines = lines.get(str(problem_num))
    if lines is None:
        print(f"The category '{category}' does not have a problem numbered #{problem_num}.")
        return None

    lines = lines.split(" ")

    max_x, max_y = 0, 0
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            if c == "@": # black stone.
                draw_stone(board, x, y, stone_size_px, is_black=True)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
            elif c == "!": # white stone.
                draw_stone(board, x, y, stone_size_px, is_black=False)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    if 0.9 < abs(max_x / max_y) < 1.1:
        pass
    elif max_x > CELLS_WIDE - 2:
        # enforces xy flipping after a certain width
        flip_xy = True
    elif max_x > 5:
        flip_xy = False

    
    if flip_xy:
        board = board.transpose(Image.TRANSPOSE)
    if flip_x:
        board = board.transpose(Image.FLIP_TOP_BOTTOM)
    if flip_y:
        board = board.transpose(Image.FLIP_LEFT_RIGHT)

    is_top = True
    is_left = True
    if flip_xy:
        placeholder = is_top
        is_top = is_left
        is_left = placeholder

        placeholder = max_x
        max_x = max_y
        max_y = placeholder

    if flip_x:
        is_top = not is_top

    if flip_y:
        is_left = not is_left

    if CELLS_WIDE >= 19:
        CELLS_WIDE = 19

    w, h = board.size
    left = 0 if is_left else w - stone_size_px * CELLS_WIDE
    right = left + stone_size_px * CELLS_WIDE
    top = 0 if is_top else h - stone_size_px * (max_y + 2)
    bottom = top + stone_size_px * (max_y + 2)
    
    board = board.crop((left, top, right, bottom))

    return board