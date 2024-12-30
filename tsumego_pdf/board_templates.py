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
    save_image: bool = False,
):
    Y_SCALE = 1.0421686747
    STONE_SIZE_IN = 0.8645833333333333
    LINE_WIDTH_IN = 1 / 48
    STAR_POINT_RADIUS_IN = 5 / 64

    # the minimum required print margin. if the program has to use
    # multiple papers to print the board, then the normal given
    # <margin_in> will be used to emulate 
    # the real edge dimensions of an actual Go board.
    # if, however, the board is small enough, the program will try
    # to squeeze it onto one piece of paper. in doing so,
    # these margins must be maintained (1/4").
    MIN_MARGIN_PX = {
        "left": 1/4 * DPI,
        "top": 1/4 * DPI,
        "right": 1/4 * DPI,
        "bottom": 1/4 * DPI,
    }

    if isinstance(board_size, tuple):
        board_width, board_height = board_size
    else:
        board_width, board_height = board_size, board_size

    if out_path is None:
        out_path = f"printable board {board_width}x{board_height}.pdf"

    if landscape and paper_size[0] < paper_size[1]:
        paper_size = (paper_size[1], paper_size[0])

    img_w = int(paper_size[0] / 72 * DPI)
    img_h = int(paper_size[1] / 72 * DPI)

    padding_in = BOARD_PADDING_PX / DPI
    board_width_in = STONE_SIZE_IN * board_width

    # draws the board.
    board, _ = draw_board(
        board_width_in,
        line_width_in=LINE_WIDTH_IN,
        star_point_radius_in=STAR_POINT_RADIUS_IN,
        board_size=board_size,
        y_scale=Y_SCALE,
        fill_color=fill_color,
    )

    if save_image:
        out_img_path = out_path[:-4] + ".png"
        new_w, new_h = int(board.size[0] * 0.25), int(board.size[1] * 0.25)
        out_board = board.resize((new_w, new_h), Image.Resampling.LANCZOS)
        out_board.save(out_img_path)

    """
    Step 2) Determines dimensions of the printout.
    """
    cell_width_px = (board.size[0] - BOARD_PADDING_PX * 2) / board_width
    cell_height_px = (board.size[1] - BOARD_PADDING_PX * 2) / board_height

    pages_needed_wide = int((
        cell_width_px * (board_width - 1)
        + MIN_MARGIN_PX["left"] 
        + MIN_MARGIN_PX["right"]
    ) // img_w + 1)

    pages_needed_high = int((
        cell_height_px * (board_height - 1)
        + MIN_MARGIN_PX["top"] 
        + MIN_MARGIN_PX["bottom"]
    ) // img_h + 1)


    """
    Step 3) Determines where the image of the board must be pasted
            in order to render a PDF that can be printed and glued
            together to be played on.
    """
    paste_coords = []

    m_l = margin_in["left"] * DPI
    m_t = margin_in["top"] * DPI
    m_r = margin_in["right"] * DPI
    m_b = margin_in["bottom"] * DPI

    if pages_needed_wide == 1 and pages_needed_high == 1:
        # centers board on the single page.
        paste_x = int((img_w - board.size[0]) / 2)
        paste_y = int((img_h - board.size[1]) / 2)
        paste_coords.append((paste_x, paste_y))

    elif pages_needed_wide > 1 and pages_needed_high > 1:
        # creates paste points to render board
        # across a 2D array of papers.
        x_off = cell_width_px / 2
        start_x = int(m_l - x_off)
        end_x = int(img_w - m_r - board.size[0] + x_off)
        step_x = (end_x - start_x) / (pages_needed_wide - 1)

        y_off = cell_height_px / 2
        start_y = int(m_t - y_off)
        end_y = int(img_h - m_b - board.size[1] + y_off)
        step_y = (end_y - start_y) / (pages_needed_high - 1)

        for page_x in range(pages_needed_wide):
            paste_x = start_x + step_x * page_x
            for page_y in range(pages_needed_high):
                paste_y = start_y + step_y * page_y
                paste_coords.append((paste_x, paste_y))

    elif pages_needed_high > 1:
        # needs several vertical pages.
        paste_x = int((img_w - board.size[0]) / 2)

        y_off = cell_height_px / 2
        start_y = int(m_t - y_off)
        end_y = int(img_h - m_b - board.size[1] + y_off)
        step_y = (end_y - start_y) / (pages_needed_high - 1)

        for page_y in range(pages_needed_high):
            paste_y = start_y + step_y * page_y
            paste_coords.append((paste_x, paste_y))
    
    else:
        # needs several horizontal pages.
        paste_y = int((img_h - board.size[1]) / 2)

        x_off = cell_width_px / 2
        start_x = int(m_l - x_off)
        end_x = int(img_w - m_r - board.size[0] + x_off)
        step_x = (end_x - start_x) / (pages_needed_wide - 1)

        for page_x in range(pages_needed_wide):
            paste_x = start_x + step_x * page_x
            paste_coords.append((paste_x, paste_y))

    paste_coords = [(int(x), int(y)) for x, y in paste_coords]

    """
    Step 4) Pastes the board and saves the page images.
    """
    temp_paths = []
    for paste_x, paste_y in paste_coords:
        page = Image.new("RGB", (img_w, img_h), (255, 255, 255))
        page.paste(board, (paste_x, paste_y))

        with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
            temp_path = temp_file.name

        page.save(temp_path)
        temp_paths.append(temp_path)

    """
    Step 5) Creates and saves the PDF.
    """
    # opens PDF writer.
    out_pdf = canvas.Canvas(out_path, pagesize=paper_size)

    scale_x = paper_size[0] / img_w
    scale_y = paper_size[1] / img_h
    scale = min(scale_x, scale_y)

    out_w = img_w * scale
    out_h = img_h * scale

    for i, temp_path in enumerate(temp_paths):
        out_pdf.drawImage(temp_path, 0, 0, width=out_w, height=out_h)
        if i < len(temp_paths) - 1:
            out_pdf.showPage()

    out_pdf.save()

    for temp_path in temp_paths:
        os.remove(temp_path)

    print(
        f"A printable {board_width}x{board_height} "
        f'Go board has been saved to "{out_path}".'
    )
