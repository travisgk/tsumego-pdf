import os
from PIL import Image, ImageDraw, ImageFont

DPI = 300

LINE_WIDTH_IN = 1/96
LINE_COLOR = (128, 128, 128)
STAR_POINT_RADIUS_IN = 1/96

TEXT_RGB = (128, 128, 128)
TEXT_HEIGHT_IN = 0.21
TEXT_PADDING_TOP_IN = 0.0625
TEXT_PADDING_BOTTOM_IN = 0

def draw_board(width_in):
    """ Returns a drawn Go board."""
    line_width = max(1, round(LINE_WIDTH_IN * DPI))

    width, height = round(width_in * DPI), round(width_in * DPI)
    image = Image.new("RGB", (width, height), "white")

    # draws lines.
    draw = ImageDraw.Draw(image)

    cell_size_px = width_in/19 * DPI

    # draws the vertical lines.
    for x in range(19):
        draw_x = round(cell_size_px/2 + x*cell_size_px)
        y0 = round(cell_size_px/2)
        y1 = round(y0 + 18*cell_size_px)
        a = (draw_x, y0 - line_width//2 + 1)
        b = (draw_x, y1 + line_width//2 - 1)
        draw.line([a, b], fill=LINE_COLOR, width=line_width)

    # draws the horizontal lines.
    for y in range(19):
        draw_y = round(cell_size_px/2 + y*cell_size_px)
        x0 = round(cell_size_px/2)
        x1 = round(x0 + 18*cell_size_px)
        a = (x0 - line_width//2 + 1, draw_y)
        b = (x1 + line_width//2 - 1, draw_y)
        draw.line([a, b], fill=LINE_COLOR, width=line_width)

    # draws the star points.
    radius_px = round(STAR_POINT_RADIUS_IN * DPI)
    STAR_POINTS = [(x, y) for x in [3, 9, 15] for y in [3, 9, 15]]
    for p in STAR_POINTS:
        x = round(cell_size_px/2 + p[0]*cell_size_px)
        y = round(cell_size_px/2 + p[1]*cell_size_px)
        bbox = (
            x - radius_px,
            y - radius_px,
            x + radius_px + radius_px%2,
            y + radius_px + radius_px%2
        )
        draw.ellipse(bbox, fill=LINE_COLOR)

    return image, draw


_GRAPHIC_PADDING_PX = 6
def create_stone_graphic(stone_size_px, is_black: bool):
    """ Returns a PIL image with the stone graphic inside. """
    OUTLINE_THICKNESS_IN = 1/128
    SCALE = 4

    # dims of output image.
    w = stone_size_px + _GRAPHIC_PADDING_PX * 2
    h = stone_size_px + _GRAPHIC_PADDING_PX * 2
    
    # stone image is drawn scaled up.
    large_size = (round(w * SCALE), round(h * SCALE))
    large_image = Image.new("RGBA", large_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(large_image)
    
    # draws a black circle.
    fill_color = "black"
    center = (large_size[0] / 2, large_size[1] / 2)
    outer_radius = int(stone_size_px/2 * SCALE)

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
        inner_radius = round(outer_radius - OUTLINE_THICKNESS_IN * SCALE * DPI)
        
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


_LAST_STONE_SIZE = None
_BLACK_STONE_IMAGE = None
_WHITE_STONE_IMAGE = None
def draw_stone(board, x, y, stone_size_px, is_black: bool):
    """ Draws a stone graphic at the given board coordinate. """

    # loads stone graphics if they haven't been loaded yet.
    global _LAST_STONE_SIZE, _BLACK_STONE_IMAGE, _WHITE_STONE_IMAGE
    if _LAST_STONE_SIZE != stone_size_px:
        _BLACK_STONE_IMAGE = create_stone_graphic(stone_size_px, is_black=True)
        _WHITE_STONE_IMAGE = create_stone_graphic(stone_size_px, is_black=False)
        _LAST_STONE_SIZE = stone_size_px

    draw_x = round(x * stone_size_px) - _GRAPHIC_PADDING_PX
    draw_y = round(y * stone_size_px) - _GRAPHIC_PADDING_PX
    img = _BLACK_STONE_IMAGE if is_black else _WHITE_STONE_IMAGE
    board.paste(img, (draw_x, draw_y), mask=img)


_FONT = None
def create_text_image(text: str):
    """ Returns an image with text drawn inside. """
    # loads font if it hasn't been done yet.
    global _FONT
    if _FONT is None:
        # loads font.
        local_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(local_dir, "font.ttf")
        _FONT = ImageFont.truetype(font_path, size=DPI/4)

    # determines the bbox that the drawn text will have.
    text_image = Image.new("RGB", (2000, 1000), (255, 255, 255))
    text_draw = ImageDraw.Draw(text_image)
    bbox = text_draw.textbbox((200, 200), text, font=_FONT)
    bbox = (bbox[0], bbox[1] - 10, bbox[2], bbox[3] + 10) # pads.

    # draws the text, then crops it out according to its bbox.
    text_draw.text((200, 200), text, font=_FONT, fill=TEXT_RGB)
    text_image = text_image.crop(bbox)
    w, h = text_image.size
    
    # scales the text down.
    height_px = TEXT_HEIGHT_IN * DPI
    ratio = w / h
    width_px = height_px * ratio

    return text_image.resize(
        (round(width_px), round(height_px)),
        Image.Resampling.LANCZOS,
    )