import os
import tempfile
import numpy as np
from PIL import Image, ImageDraw
import reportlab.lib.pagesizes
from reportlab.pdfgen import canvas
from .draw_game.board_graphics import DPI, BOARD_PADDING_PX, LINE_COLOR, draw_board


def create_blank_template(
    paper_size: tuple,  # 72 DPI
    board_width_in=2.5,
    out_path: str = None,
    landscape: bool = False,
    margin_in: dict = {"left": 0.5, "top": 0.5, "right": 0.5, "bottom": 0.5},
    board_size: int = 19,
    boards_per_row: int = 2,
    boards_per_col: int = 3,
    num_pages: int = 1,
    draw_bbox_around_diagrams: bool = True,
):
    """
    Saves a PDF of a bunch of blank Go boards for printout.

    Parameters:
        paper_size (tuple): the output PDF size in pixels (assuming 72 DPI).
        out_path (str): the path the PDF will be saved to.
        landscape (bool): if True, the paper will be oriented landscape.
        margin_in (dict): the print margins in inches.
        board_size (int): the width/height of the board in stones (e.g. 9, 13, 19).
        boards_per_row (int): the number of blank board templates per row.
        boards_per_col (int): the number of blank board templates per column.
        num_pages (int): the number of copies of the page in the PDF.
    """
    line_width_in = 1 / 96  #  relative to 1 inch.
    star_point_radius_in = 1 / 48  #  relative to 1 inch.

    if out_path is None:
        out_path = "templates 19x19.pdf"

    if landscape and paper_size[0] < paper_size[1]:
        paper_size = (paper_size[1], paper_size[0])

    img_w = int(paper_size[0] / 72 * DPI)
    img_h = int(paper_size[1] / 72 * DPI)
    page = Image.new("RGB", (img_w, img_h), (255, 255, 255))

    m_l, m_t, m_r, m_b = (
        margin_in["left"] * DPI,
        margin_in["top"] * DPI,
        margin_in["right"] * DPI,
        margin_in["bottom"] * DPI,
    )

    if boards_per_row == 1 and boards_per_col == 1:
        board_width_in = min(img_w - m_l - m_r, img_h - m_t - m_b) / DPI

    board, _ = draw_board(
        width_in=board_width_in,
        line_width_in=line_width_in,
        star_point_radius_in=star_point_radius_in,
        board_size=board_size,
    )

    if boards_per_col > 1:
        col_spacing = ((img_w - m_l - m_r) - board.size[0] * boards_per_col) / (
            boards_per_col - 1
        )
        offset_x = 0
    else:
        col_spacing = 0  #  will be centered.
        offset_x = ((img_w - m_l - m_r) - board.size[0]) / 2

    if boards_per_row > 1:
        row_spacing = ((img_h - m_t - m_b) - board.size[1] * boards_per_row) / (
            boards_per_row - 1
        )
        offset_y = 0
    else:
        row_spacing = 0  #  will be centered.
        offset_y = ((img_h - m_t - m_b) - board.size[1]) / 2

    draw = ImageDraw.Draw(page) if draw_bbox_around_diagrams else None

    for col in range(boards_per_col):
        col_x = m_l + offset_x + (board.size[0] + col_spacing) * col
        for row in range(boards_per_row):
            row_y = m_t + offset_y + (board.size[1] + row_spacing) * row

            page.paste(board, (int(col_x), int(row_y)), mask=board)
            # print(f"{col_x}, {row_y}")
            if draw_bbox_around_diagrams:
                tl = (col_x - m_l, row_y - m_t)
                tr = (col_x + board.size[0] + m_r, row_y - m_t)
                br = (col_x + board.size[0] + m_r, row_y + board.size[1] + m_b)
                bl = (col_x - m_l, row_y + board.size[1] + m_b)

                draw.line((tl[0], tl[1], tr[0], tr[1]), width=3, fill=LINE_COLOR)
                draw.line((tr[0], tr[1], br[0], br[1]), width=3, fill=LINE_COLOR)
                draw.line((bl[0], bl[1], br[0], br[1]), width=3, fill=LINE_COLOR)
                draw.line((bl[0], bl[1], tl[0], tl[1]), width=3, fill=LINE_COLOR)

    """
    Step 2) Creates PDF.
    """
    # saves page to a temp file.
    with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
        temp_path = temp_file.name

    page.save(temp_path)

    # opens PDF writer.
    out_pdf = canvas.Canvas(out_path, pagesize=paper_size)

    scale_x = paper_size[0] / img_w
    scale_y = paper_size[1] / img_h
    scale = min(scale_x, scale_y)

    out_w = img_w * scale
    out_h = img_h * scale

    for _ in range(num_pages):
        out_pdf.drawImage(temp_path, 0, 0, width=out_w, height=out_h)
        out_pdf.showPage()

    out_pdf.save()

    os.remove(temp_path)

    print(
        f"A PDF of blank {board_width}x{board_height} "
        f'Go boards has been saved to "{out_path}".'
    )


def create_portable_board(
    paper_size: tuple,  # 72 DPI
    out_path: str = None,
    landscape: bool = False,
    margin_in: dict = {
        "left": 7 / 8,
        "top": 29 / 32,
        "right": 7 / 8,
        "bottom": 29 / 32,
    },
    board_size=19,
    fill_color=(0, 0, 0),
):
    if isinstance(board_size, tuple):
        board_width, board_height = board_size
    else:
        board_width, board_height = board_size, board_size

    y_scale = 1.0421686747
    stone_size_in = 0.8645833333333333
    line_width_in = 1 / 48
    star_point_radius_in = 1 / 16

    if out_path is None:
        out_path = f"printable board {board_width}x{board_height}.pdf"

    if landscape and paper_size[0] < paper_size[1]:
        paper_size = (paper_size[1], paper_size[0])

    img_w = int(paper_size[0] / 72 * DPI)
    img_h = int(paper_size[1] / 72 * DPI)

    page = Image.new("RGB", (img_w, img_h), (255, 255, 255))

    padding_in = BOARD_PADDING_PX / DPI

    board_width_in = stone_size_in * board_width

    board, _ = draw_board(
        board_width_in,
        line_width_in=line_width_in,
        star_point_radius_in=star_point_radius_in,
        board_size=board_size,
        y_scale=y_scale,
        fill_color=fill_color,
    )

    c = -(DPI * stone_size_in / 2)
    if stone_size_in * DPI > img_w:
        m_l = margin_in["left"] * DPI
        paste_x = int(c + m_l)
    else:
        # horizontally centers the board on the page.
        paste_x = int((img_w - board.size[0]) / 2)

    if stone_size_in * DPI * y_scale > img_h:
        m_t = margin_in["top"] * DPI
        paste_y = int(c + m_t)
    else:
        # vertically centers the board on the page.
        paste_y = int((img_h - board.size[1]) / 2)

    page.paste(board, (paste_x, paste_y))

    """
    Step 2) Creates PDF.
    """
    # saves page to a temp file.
    with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
        temp_path = temp_file.name

    page.save(temp_path)

    # opens PDF writer.
    out_pdf = canvas.Canvas(out_path, pagesize=paper_size)

    scale_x = paper_size[0] / img_w
    scale_y = paper_size[1] / img_h
    scale = min(scale_x, scale_y)

    out_w = img_w * scale
    out_h = img_h * scale

    out_pdf.drawImage(temp_path, 0, 0, width=out_w, height=out_h)

    # for _ in range(num_pages):
    #    out_pdf.drawImage(temp_path, 0, 0, width=out_w, height=out_h)
    #    out_pdf.showPage()

    out_pdf.save()

    os.remove(temp_path)

    print(
        f"A printable {board_width}x{board_height} "
        f'Go board has been saved to "{out_path}".'
    )
