"""
tsumego_pdf.draw_game.board_graphics.py
---
This file contains constants and functions to create and store
graphical components for the drawing of diagrams.
"""

import os
from PIL import Image, ImageDraw, ImageFont
from tsumego_pdf.puzzles.playout import STONE_TO_NUM, BLACK_STONES, WHITE_STONES

DPI = 300

LINE_COLOR = (128, 128, 128)

TEXT_PADDING_TOP_IN = 1 / 16
TEXT_PADDING_BOTTOM_IN = 0
BOARD_PADDING_PX = 2

_STONE_OUTLINE_COLOR = (0, 0, 0)
_BLACK_STONE_COLOR = (0, 0, 0)
_WHITE_STONE_COLOR = (255, 255, 255)
_BOARD_COLOR = (255, 255, 255)

_GRAPHIC_PADDING_PX = 6


def _create_stone_graphic(stone_size_px, is_black: bool, outline_thickness_in):
    """Returns a PIL image with the stone graphic inside."""
    SCALE = 4

    # dims of output image.
    w = stone_size_px + _GRAPHIC_PADDING_PX * 2
    h = stone_size_px + _GRAPHIC_PADDING_PX * 2

    # stone image is drawn scaled up.
    large_size = (int(w * SCALE), int(h * SCALE))
    large_image = Image.new("RGBA", large_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(large_image)

    # draws a black circle.
    fill_color = _STONE_OUTLINE_COLOR
    center = (large_size[0] / 2, large_size[1] / 2)
    outer_radius = int(stone_size_px / 2 * SCALE)

    bbox = (
        center[0] - outer_radius,
        center[1] - outer_radius,
        center[0] + outer_radius,
        center[1] + outer_radius,
    )
    draw.ellipse(bbox, fill=fill_color)

    if not is_black or _STONE_OUTLINE_COLOR != _BLACK_STONE_COLOR:
        # draws a smaller white circle on top.
        fill_color = _BLACK_STONE_COLOR if is_black else _WHITE_STONE_COLOR
        inner_radius = max(1, int(outer_radius - outline_thickness_in * SCALE * DPI))

        bbox = (
            center[0] - inner_radius,
            center[1] - inner_radius,
            center[0] + inner_radius,
            center[1] + inner_radius,
        )
        draw.ellipse(bbox, fill=fill_color)

    return large_image.resize(
        (int(w), int(h)),
        Image.Resampling.LANCZOS,
    )


def _create_star_point_graphic(
    cell_width_px, cell_height_px, star_point_radius_in, fill_color=(0, 0, 0, 255)
):
    SCALE = 4
    result = Image.new(
        "RGBA",
        (cell_width_px * SCALE, cell_height_px * SCALE),
        (255, 255, 255, 0),
    )
    draw = ImageDraw.Draw(result)

    radius = star_point_radius_in * DPI * SCALE
    left = int(result.size[0] / 2 - radius)
    top = int(result.size[1] / 2 - radius)
    right = int(result.size[0] / 2 + radius)
    bottom = int(result.size[1] / 2 + radius)

    bbox = (left, top, right, bottom)
    draw.ellipse(bbox, fill=fill_color)

    return result.resize((cell_width_px, cell_height_px), resample=Image.LANCZOS)


_STAR_POINT_GRAPHIC = None
_LAST_CELL_SIZE = None


def draw_board(
    width_in,
    line_width_in=1 / 96,
    star_point_radius_in=1 / 48,
    board_size=19,
    y_scale=1.0,
    fill_color=LINE_COLOR,
    star_points=None,
):
    """Returns a drawn Go board."""
    global _STAR_POINT_GRAPHIC, _LAST_CELL_SIZE, _LAST_FACTOR
    ANTIALIAS_SIZE = 128

    """
    Step 1) Sets up variables.
    """
    # determines board width and height.
    if isinstance(board_size, tuple):
        board_width, board_height = board_size
    else:
        board_width, board_height = board_size, board_size

    cell_width_in = width_in / board_width
    cell_height_in = cell_width_in * y_scale
    height_in = cell_height_in * board_height
    cell_width_px = int(cell_width_in * DPI)
    cell_height_px = int(cell_height_in * DPI)

    line_width = max(1, int(line_width_in * DPI))

    OFF = BOARD_PADDING_PX

    img_width = int(width_in * DPI) + OFF * 2
    img_height = int(height_in * DPI) + OFF * 2
    image = Image.new("RGB", (img_width, img_height), _BOARD_COLOR)

    """
    Step 2) Draws lines.
    """
    # begins drawing lines.
    draw = ImageDraw.Draw(image)

    # draws the vertical lines.
    for x in range(board_width):
        draw_x = int(cell_width_px / 2 + x * cell_width_px)
        y0 = int(cell_height_px / 2)
        y1 = int(y0 + ((board_height - 1) * cell_height_px))
        a = (draw_x + OFF, y0 + OFF - line_width // 2 + 1)
        b = (draw_x + OFF, y1 + OFF + line_width // 2 - 1)

        draw.line([a, b], fill=fill_color, width=line_width)

    # draws the horizontal lines.
    for y in range(board_height):
        draw_y = int(cell_height_px / 2 + y * cell_height_px)
        x0 = int(cell_width_px / 2)
        x1 = int(x0 + (board_width - 1) * cell_width_px)
        a = (OFF + x0 - line_width // 2 + 1, draw_y + OFF)
        b = (OFF + x1 + line_width // 2 - 1, draw_y + OFF)
        draw.line([a, b], fill=fill_color, width=line_width)

    """
    Step 2) Creates the star point image.
    """
    if line_width % 2 == 1:
        star_point_size = cell_width_px + (1 - (cell_width_px % 2))
        px_offset = 0
    else:
        star_point_size = cell_width_px + (cell_width_px % 2)
        px_offset = 1 - cell_width_px % 2

    if _STAR_POINT_GRAPHIC is None or _STAR_POINT_GRAPHIC.size[0] != star_point_size:
        _STAR_POINT_GRAPHIC = _create_star_point_graphic(
            cell_width_px,
            cell_height_px,
            star_point_radius_in=star_point_radius_in,
            fill_color=fill_color,
        )

    """
    Step 3) Determines the board coords for the star points.
    """
    radius_px = int(star_point_radius_in * DPI)

    x_horiz_star_coords = []
    y_vertical_star_coords = []

    if board_width % 2 == 1 and board_width >= 9:
        center_point_x = board_width // 2
    else:
        center_point_x = None

    if board_height % 2 == 1 and board_height >= 9:
        center_point_y = board_height // 2
    else:
        center_point_y = None

    x_horiz_star_coords = []
    y_horiz_star_coords = []

    if board_width >= 17 and center_point_x is not None:
        x_horiz_star_coords.append(center_point_x)

    if board_height >= 17 and center_point_y is not None:
        y_horiz_star_coords.append(center_point_y)

    if board_width >= 12:
        x_horiz_star_coords.extend([3, board_width - 4])

    if board_height >= 12:
        y_horiz_star_coords.extend([3, board_height - 4])

    if star_points is None:
        star_points = []

        if center_point_x is not None and center_point_y is not None:
            star_points.append((center_point_x, center_point_y))

        for star_x in x_horiz_star_coords:
            for star_y in y_horiz_star_coords:
                star_points.append((star_x, star_y))

    SCALE = 4
    if cell_width_px >= ANTIALIAS_SIZE:
        # draws star points with antialiasing.
        out_w, out_h = img_width * SCALE, img_height * SCALE
        comp = Image.new("RGBA", (out_w, out_h), (255, 255, 255, 0))
        draw = ImageDraw.Draw(comp)

        for x, y in star_points:
            p_x = (
                int(cell_width_px / 2 + x * cell_width_px)
                + OFF
                + (radius_px * SCALE % 2)
            )
            p_y = (
                int(cell_height_px / 2 + y * cell_height_px)
                + OFF
                + (radius_px * SCALE % 2)
            )

            r = radius_px * SCALE + (1 - ((radius_px * SCALE) % 2))
            l = line_width * SCALE
            p_x = int(SCALE * (cell_width_px / 2 + x * cell_width_px + OFF)) + r % 2
            p_y = int(SCALE * (cell_height_px / 2 + y * cell_height_px + OFF)) + r % 2

            bbox = (
                p_x - r,
                p_y - r,
                p_x + r + (l + 1) % 2,
                p_y + r + (l + 1) % 2,
            )

            draw.ellipse(bbox, fill=fill_color)

        comp = comp.resize((img_width, img_height), Image.Resampling.LANCZOS)
        image = Image.alpha_composite(image, comp)
    else:
        # draws star points without antialiasing.
        for x, y in star_points:
            p_x = int(cell_width_px / 2 + x * cell_width_px) + OFF + (radius_px % 2)
            p_y = int(cell_height_px / 2 + y * cell_height_px) + OFF + (radius_px % 2)

            r = radius_px + (1 - (radius_px % 2))
            bbox = (
                p_x - radius_px,
                p_y - radius_px,
                p_x + radius_px + (line_width + 1) % 2,
                p_y + radius_px + (line_width + 1) % 2,
            )
            draw.ellipse(bbox, fill=fill_color)

    return image, draw


def _load_mark_image(stone_size_px, is_black: bool, solution_mark: str):
    local_dir = os.path.dirname(os.path.abspath(__file__))

    if is_black:
        file_name = f"{solution_mark}-black.png"
    else:
        file_name = f"{solution_mark}-white.png"

    graphic = Image.open(os.path.join(local_dir, "res", file_name))
    new_size = (stone_size_px, stone_size_px)

    return graphic.resize(new_size, Image.Resampling.LANCZOS)


_FONT = None
_NUMS_FONT = None


def create_text_image(
    text: str,
    rgb_fill: tuple,
    text_height_in=0.21,
    transparent: bool = False,
    is_num: bool = False,
):
    """Returns an image with text drawn inside."""
    # loads font if it hasn't been done yet.
    global _FONT, _NUMS_FONT
    if _FONT is None:
        # loads font.
        local_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(local_dir, "res", "font.ttf")
        nums_font_path = os.path.join(local_dir, "res", "nums.ttf")
        _FONT = ImageFont.truetype(font_path, size=DPI / 4)
        _NUMS_FONT = ImageFont.truetype(nums_font_path, size=DPI / 4)

    # determines the bbox that the drawn text will have.
    if transparent:
        text_image = Image.new("RGBA", (2000, 1000), (255, 255, 255, 0))
        if len(rgb_fill) == 3:
            rgb_fill = (*rgb_fill[:3], 255)
    else:
        text_image = Image.new("RGB", (2000, 1000), (255, 255, 255))
    text_draw = ImageDraw.Draw(text_image)

    draw_font = _NUMS_FONT if is_num else _FONT

    bbox = text_draw.textbbox((200, 200), text, font=draw_font)
    bbox = (bbox[0], bbox[1] - 10, bbox[2], bbox[3] + 10)  # pads.

    # draws the text, then crops it out according to its bbox.
    text_draw.text((200, 200), text, font=draw_font, fill=rgb_fill)
    text_image = text_image.crop(bbox)
    w, h = text_image.size

    if w == 0 or h == 0:
        return Image.new("RGBA", (10, 10), (255, 255, 255, 0))

    # scales the text down.
    height_px = text_height_in * DPI
    ratio = w / h
    width_px = height_px * ratio

    return text_image.resize(
        (int(width_px), int(height_px)),
        Image.Resampling.LANCZOS,
    )


_NUMBERS = None
_INSIDE_NUMBERS_DARK = None  # inside white stone.
_INSIDE_NUMBERS_LIGHT = None  # inside black stone.

_circle = None


def _create_stone_numbers_for_key(stone_size_px):
    global _NUMBERS, _INSIDE_NUMBERS_DARK, _INSIDE_NUMBERS_LIGHT

    _NUMBERS = []
    _INSIDE_NUMBERS_DARK = []
    _INSIDE_NUMBERS_LIGHT = []

    DARK_RGB = (0, 0, 0)
    LIGHT_RGB = (255, 255, 255)
    MAX_NUM = 12  # inclusive.
    INSIDE_SCALE = 0.7

    stone_size_in = stone_size_px / DPI
    scaled = stone_size_in * INSIDE_SCALE

    def make_num(i, rgb, size_in, add_circle: bool = False):
        global _circle
        img = create_text_image(str(i), rgb, size_in, True, is_num=True)
        w, h = img.size
        d = int(stone_size_in * DPI)

        result = Image.new("RGBA", (d, d), (255, 255, 255, 0))

        if add_circle:
            if _circle is None:
                # adds a white transparent circle underneath.
                SCALE = 2
                _circle = Image.new("RGBA", (d * SCALE, d * SCALE), (255, 255, 255, 0))
                draw = ImageDraw.Draw(_circle)

                NUM_FADES = 23

                START_ALPHA = 10
                END_ALPHA = 255
                alpha_step = (END_ALPHA - START_ALPHA) / (NUM_FADES - 1)

                START_DIA = d * SCALE - 4
                END_DIA = d * SCALE * 0.61
                dia_step = (END_DIA - START_DIA) / (NUM_FADES - 1)
                for i in range(NUM_FADES):
                    alpha = START_ALPHA + int(alpha_step * i)
                    dia = START_DIA + int(dia_step * i)
                    fill = (255, 255, 255, alpha)
                    m_x = (d * SCALE - dia) / 2
                    m_y = (d * SCALE - dia) / 2
                    draw.ellipse(
                        (
                            int(m_x),
                            int(m_y),
                            int(d * SCALE - m_x),
                            int(d * SCALE - m_y),
                        ),
                        fill=fill,
                    )

                diameter = d
                _circle = _circle.resize(
                    (int(diameter), int(diameter)),
                    Image.Resampling.LANCZOS,
                )
            draw_x = int((d - _circle.size[0]) / 2)
            draw_y = int((d - _circle.size[1]) / 2)

            result.paste(_circle, (draw_x, draw_y), mask=_circle)

        draw_x = int((d - w) / 2)
        draw_y = int((d - h) / 2)
        result.paste(img, (draw_x, draw_y), mask=img)

        return result

    for i in range(MAX_NUM):
        _NUMBERS.append(make_num(i, DARK_RGB, scaled, add_circle=True))
        _INSIDE_NUMBERS_DARK.append(make_num(i, DARK_RGB, scaled))
        _INSIDE_NUMBERS_LIGHT.append(make_num(i, LIGHT_RGB, scaled))


_BLACK_STONE_IMAGE = None
_WHITE_STONE_IMAGE = None

_SOLUTION_MARK = None
_SOLUTION_BLACK_IMAGE = None
_SOLUTION_WHITE_IMAGE = None


def refresh_stone_graphics(stone_size_px, solution_mark: str, outline_thickness_in):
    # loads stone graphics if they haven't been loaded yet.
    global _BLACK_STONE_IMAGE, _WHITE_STONE_IMAGE
    global _SOLUTION_MARK, _SOLUTION_BLACK_IMAGE, _SOLUTION_WHITE_IMAGE
    if _BLACK_STONE_IMAGE is None or _BLACK_STONE_IMAGE.size[0] != stone_size_px:
        _BLACK_STONE_IMAGE = _create_stone_graphic(
            stone_size_px,
            is_black=True,
            outline_thickness_in=outline_thickness_in,
        )
        _WHITE_STONE_IMAGE = _create_stone_graphic(
            stone_size_px,
            is_black=False,
            outline_thickness_in=outline_thickness_in,
        )
        _create_stone_numbers_for_key(stone_size_px)

    if (
        _SOLUTION_MARK != solution_mark
        or _SOLUTION_BLACK_IMAGE.size[0] != stone_size_px
    ):
        _SOLUTION_BLACK_IMAGE = _load_mark_image(
            stone_size_px, is_black=True, solution_mark=solution_mark
        )
        _SOLUTION_WHITE_IMAGE = _load_mark_image(
            stone_size_px, is_black=False, solution_mark=solution_mark
        )


def draw_stone(board, x, y, stone_size_px, is_black: bool, outline_thickness_in):
    """Draws a stone graphic at the given board coordinate."""

    OFF = BOARD_PADDING_PX

    if stone_size_px > _GRAPHIC_PADDING_PX:
        draw_x = int(x * stone_size_px) - _GRAPHIC_PADDING_PX + OFF
        draw_y = int(y * stone_size_px) - _GRAPHIC_PADDING_PX + OFF
        img = _BLACK_STONE_IMAGE if is_black else _WHITE_STONE_IMAGE
        board.paste(img, (draw_x, draw_y), mask=img)
    else:
        draw_x = int(x * stone_size_px) + OFF
        draw_y = int(y * stone_size_px) + OFF
        r = stone_size_px / 2
        bbox = (int(draw_x - r), int(draw_y - r), int(draw_x + r), int(draw_y + r))
        draw = ImageDraw.draw(board)
        draw.ellipse(bbox, fill=_BLACK_STONE_COLOR if is_black else (128, 128, 255))


def draw_cover(width_px, height_px, booklet_cover: str):
    """Returns a PIL image for the cover of a booklet."""

    cover = Image.new("RGB", (width_px, height_px), (255, 255, 255))
    local_dir = os.path.dirname(os.path.abspath(__file__))
    graphic_path = os.path.join(local_dir, "res", f"{booklet_cover}-cover.png")
    cover_graphic = Image.open(graphic_path)

    span = width_px // 2
    img_width = span * 0.7
    ratio = cover_graphic.size[1] / cover_graphic.size[0]
    img_height = img_width * ratio

    dist = (span - img_width) / 2

    cover_graphic = cover_graphic.resize(
        (int(img_width), int(img_height)),
        Image.Resampling.LANCZOS,
    )

    paste_x = int(width_px / 2 + dist)
    paste_y = int((height_px / 3) - img_height / 2)  # int(height_px / 5)

    cover.paste(cover_graphic, (paste_x, paste_y), mask=cover_graphic)

    w, h = cover.size
    cover = cover.crop((w // 2, 0, w, h))

    return cover


def draw_mark(board, x, y, stone_size_px, is_black: bool):
    OFF = BOARD_PADDING_PX
    draw_x = int(x * stone_size_px) + OFF
    draw_y = int(y * stone_size_px) + OFF
    img = _SOLUTION_BLACK_IMAGE if is_black else _SOLUTION_WHITE_IMAGE
    board.paste(img, (draw_x, draw_y), mask=img)


def draw_key_number(board, x, y, stone_size_px, char: str):
    OFF = BOARD_PADDING_PX
    draw_x = int(x * stone_size_px) + OFF
    draw_y = int(y * stone_size_px) + OFF

    if char in "123456789":
        img = _NUMBERS[int(char)]
    elif char in BLACK_STONES:
        img = _INSIDE_NUMBERS_LIGHT[STONE_TO_NUM[char]]
    else:
        img = _INSIDE_NUMBERS_DARK[STONE_TO_NUM[char]]

    board.paste(img, (draw_x, draw_y), mask=img)
