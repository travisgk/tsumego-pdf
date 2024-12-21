import os
from PIL import Image, ImageDraw, ImageFont

DPI = 300

LINE_COLOR = (128, 128, 128)

TEXT_PADDING_TOP_IN = 1 / 16
TEXT_PADDING_BOTTOM_IN = 0
BOARD_PADDING_PX = 2

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
    fill_color = "black"
    center = (large_size[0] / 2, large_size[1] / 2)
    outer_radius = int(stone_size_px / 2 * SCALE)

    bbox = (
        center[0] - outer_radius,
        center[1] - outer_radius,
        center[0] + outer_radius,
        center[1] + outer_radius,
    )
    draw.ellipse(bbox, fill=fill_color)

    if not is_black:
        # draws a smaller white circle on top.
        fill_color = "white"
        inner_radius = int(outer_radius - outline_thickness_in * SCALE * DPI)

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


def _create_star_point_graphic(stone_size_px, star_point_radius_in):
    """Returns a PIL image with the stone graphic inside."""
    SCALE = 4

    # dims of output image.
    w = stone_size_px + _GRAPHIC_PADDING_PX * 2
    h = stone_size_px + _GRAPHIC_PADDING_PX * 2

    # stone image is drawn scaled up.
    large_size = (int(w * SCALE), int(h * SCALE))
    large_image = Image.new("RGBA", large_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(large_image)

    # draws a circle.
    fill_color = LINE_COLOR
    center = (large_size[0] // 2, large_size[1] // 2)

    star_point_radius = int(star_point_radius_in * DPI * SCALE)

    bbox = (
        center[0] - star_point_radius,
        center[1] - star_point_radius,
        center[0] + star_point_radius,
        center[1] + star_point_radius,
    )
    draw.ellipse(bbox, fill=fill_color)

    return large_image.resize(
        (int(w), int(h)),
        Image.Resampling.LANCZOS,
    )

_STAR_POINT_GRAPHIC = None
def draw_board(width_in, line_width_in=1/96, star_point_radius_in=1/48):
    """Returns a drawn Go board."""
    global _STAR_POINT_GRAPHIC
    
    cell_size_px = width_in / 19 * DPI

    if _STAR_POINT_GRAPHIC is None:
        _STAR_POINT_GRAPHIC = _create_star_point_graphic(
            cell_size_px, star_point_radius_in
        )

    line_width = max(1, int(line_width_in * DPI))

    OFF = BOARD_PADDING_PX

    width = int(width_in * DPI) + OFF * 2
    height = int(width_in * DPI) + OFF * 2
    image = Image.new("RGBA", (width, height), (255, 255, 255, 255))

    # draws lines.
    draw = ImageDraw.Draw(image)

    # draws the vertical lines.
    for x in range(19):
        draw_x = int(cell_size_px / 2 + x * cell_size_px)
        y0 = int(cell_size_px / 2)
        y1 = int(y0 + 18 * cell_size_px)
        a = (draw_x + OFF, y0 + OFF - line_width // 2 + 1)
        b = (draw_x + OFF, y1 + OFF + line_width // 2 - 1)
        draw.line([a, b], fill=LINE_COLOR, width=line_width)

    # draws the horizontal lines.
    for y in range(19):
        draw_y = int(cell_size_px / 2 + y * cell_size_px)
        x0 = int(cell_size_px / 2)
        x1 = int(x0 + 18 * cell_size_px)
        a = (OFF + x0 - line_width // 2 + 1, draw_y + OFF)
        b = (OFF + x1 + line_width // 2 - 1, draw_y + OFF)
        draw.line([a, b], fill=LINE_COLOR, width=line_width)

    # draws the star points.
    radius_px = int(star_point_radius_in * DPI)
    STAR_POINTS = [(x, y) for x in [3, 9, 15] for y in [3, 9, 15]]

    
    
    ANTIALIAS_SIZE = 128
    if cell_size_px >= ANTIALIAS_SIZE:
        comp = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    else:
        comp = None

    for x, y in STAR_POINTS:
        if cell_size_px >= ANTIALIAS_SIZE:
            draw_x = int(x * cell_size_px) - _GRAPHIC_PADDING_PX + OFF
            draw_y = int(y * cell_size_px) - _GRAPHIC_PADDING_PX + OFF
            comp.paste(
                _STAR_POINT_GRAPHIC,
                (draw_x, draw_y),
                mask=_STAR_POINT_GRAPHIC,
            )
        else:
            p_x = int(cell_size_px / 2 + x * cell_size_px) + OFF
            p_y = int(cell_size_px / 2 + y * cell_size_px) + OFF
            bbox = (
                p_x - radius_px,
                p_y - radius_px,
                p_x + radius_px + (radius_px % 2),
                p_y + radius_px + (radius_px % 2),
            )
            draw.ellipse(bbox, fill=LINE_COLOR)

    if cell_size_px >= ANTIALIAS_SIZE:
        image = Image.alpha_composite(image, comp)

    return image, draw





def _load_mark_image(stone_size_px, is_black: bool, solution_mark: str):
    local_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = f"{solution_mark}-black.png" if is_black else f"{solution_mark}-white.png"
    graphic = Image.open(os.path.join(local_dir, file_name))
    new_size = (stone_size_px, stone_size_px)

    return graphic.resize(new_size, Image.Resampling.LANCZOS)


_BLACK_STONE_IMAGE = None
_WHITE_STONE_IMAGE = None

def draw_stone(board, x, y, stone_size_px, is_black: bool, outline_thickness_in):
    """Draws a stone graphic at the given board coordinate."""

    # loads stone graphics if they haven't been loaded yet.
    global _BLACK_STONE_IMAGE, _WHITE_STONE_IMAGE
    if _BLACK_STONE_IMAGE is None:
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

    OFF = BOARD_PADDING_PX
    draw_x = int(x * stone_size_px) - _GRAPHIC_PADDING_PX + OFF
    draw_y = int(y * stone_size_px) - _GRAPHIC_PADDING_PX + OFF
    img = _BLACK_STONE_IMAGE if is_black else _WHITE_STONE_IMAGE
    board.paste(img, (draw_x, draw_y), mask=img)

_SOLUTION_MARK = None
_SOLUTION_BLACK_IMAGE = None
_SOLUTION_WHITE_IMAGE = None

def draw_mark(board, x, y, stone_size_px, is_black: bool, solution_mark: str):
    global _SOLUTION_MARK, _SOLUTION_BLACK_IMAGE, _SOLUTION_WHITE_IMAGE
    if _SOLUTION_MARK != solution_mark:
        _SOLUTION_BLACK_IMAGE = _load_mark_image(
            stone_size_px, is_black=True, solution_mark=solution_mark
        )
        _SOLUTION_WHITE_IMAGE = _load_mark_image(
            stone_size_px, is_black=False, solution_mark=solution_mark
        )

    OFF = BOARD_PADDING_PX
    draw_x = int(x * stone_size_px) + OFF
    draw_y = int(y * stone_size_px) + OFF
    img = _SOLUTION_BLACK_IMAGE if is_black else _SOLUTION_WHITE_IMAGE
    board.paste(img, (draw_x, draw_y), mask=img)


_FONT = None


def create_text_image(text: str, rgb_fill: tuple, text_height_in=0.21):
    """Returns an image with text drawn inside."""
    # loads font if it hasn't been done yet.
    global _FONT
    if _FONT is None:
        # loads font.
        local_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(local_dir, "font.ttf")
        _FONT = ImageFont.truetype(font_path, size=DPI / 4)

    # determines the bbox that the drawn text will have.
    text_image = Image.new("RGB", (2000, 1000), (255, 255, 255))
    text_draw = ImageDraw.Draw(text_image)
    bbox = text_draw.textbbox((200, 200), text, font=_FONT)
    bbox = (bbox[0], bbox[1] - 10, bbox[2], bbox[3] + 10)  # pads.

    # draws the text, then crops it out according to its bbox.
    text_draw.text((200, 200), text, font=_FONT, fill=rgb_fill)
    text_image = text_image.crop(bbox)
    w, h = text_image.size

    # scales the text down.
    height_px = text_height_in * DPI
    ratio = w / h
    width_px = height_px * ratio

    return text_image.resize(
        (int(width_px), int(height_px)),
        Image.Resampling.LANCZOS,
    )
