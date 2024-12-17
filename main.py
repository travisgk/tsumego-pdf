from PIL import Image, ImageDraw
import reportlab.lib.pagesizes
from reportlab.pdfgen import canvas
from draw_game.diagram import DPI, get_problems, calc_stone_size, make_diagram
from create_pdf import png_to_pdf

MARGIN_LEFT_IN = 0.5
MARGIN_TOP_IN = 0.5
MARGIN_RIGHT_IN = 0.5
MARGIN_BOTTOM_IN = 0.5

def create_pages(
    page_size,
    collection,
    problem_nums=None,
    color_to_play: str="black",
    random_flip_xy: bool=True,
    random_flip_x: bool=True,
    random_flip_y: bool=True,
    include_text: bool=True,
    placement_method: str="block",
    landscape: bool=False,
    num_columns: int=2,
    column_spacing_in=0.5,
    spacing_below_in=0.5,
):
    """
    Parameters:
        color_to_play (str): "default", "black", "white" or "random".
    """
    problems = get_problems()
    if problems.get(collection) is None:
        print(
            f"'{collection}'' is not an available collection."
            "Only the following are accepted:"
        )
        for key in problems.keys():
            print(f"\t- \"{key}\"")

        return None

    w_in, h_in = page_size[0] / 72, page_size[1] / 72
    if landscape and w_in < h_in:
        placeholder = w_in
        w_in = h_in
        h_in = placeholder

    w, h = w_in * DPI, h_in * DPI

    # calculates margins.
    m_l, m_t = MARGIN_LEFT_IN * DPI, MARGIN_TOP_IN * DPI
    m_r, m_b = MARGIN_RIGHT_IN * DPI, MARGIN_BOTTOM_IN * DPI

    colspan = column_spacing_in * DPI
    spacing_below = spacing_below_in * DPI
    
    col_width_in = (
        w_in - MARGIN_LEFT_IN - MARGIN_RIGHT_IN 
        - column_spacing_in*(num_columns-1)
    ) / num_columns
    col_width = col_width_in * DPI

    
        # spacing_below = round(stone_size_px * (int(spacing_below / stone_size_px) + 1))

    col_x = [round(m_l + i*(col_width + colspan)) for i in range(num_columns)]


    # generates diagrams for all the problems and places them in the image.
    if problem_nums is None:
        problem_nums = [i for i in range(1, len(get_problems()[collection]) + 1)]

    pages = []
    
    current_col = 0
    current_y = m_t

    page = Image.new("RGB", (round(w), round(h)), (255, 255, 255))

    calc_stone_size(col_width_in)

    for problem_num in problem_nums:
        diagram = make_diagram(
            collection,
            problem_num,
            col_width_in,
            color_to_play=color_to_play,
            random_flip_xy=random_flip_xy,
            random_flip_x=random_flip_x,
            random_flip_y=random_flip_y,
            placement_method=placement_method,
            include_text=include_text,
        )

        next_y = current_y + diagram.size[1]

        if next_y > h - m_b:
            current_col += 1
            current_y = m_t

            if current_col >= num_columns:
                # TODO: add image to .pdf
                pages.append(page)
                # ---
                # next page
                page = Image.new("RGB", (round(w), round(h)), (255, 255, 255))

                current_col = 0

        if placement_method == "block":
            stone_size_px = calc_stone_size(col_width_in)
            paste_y = round(stone_size_px * (int(current_y / stone_size_px) + 1))
        else:
            paste_y = round(current_y)
        page.paste(diagram, (col_x[current_col], paste_y))
        current_y += diagram.size[1] + spacing_below

    pages.append(page)
    return pages


def main():
    page_size = reportlab.lib.pagesizes.letter
    """
    - "cho-elementary"
    - "cho-intermediate"
    - "cho-advanced"
    - "gokyo-shumyo"
    - "xuanxuan-qijing"
    - "igo-hatsuyoron"
    """

    pages = create_pages(
        page_size,
        "cho-elementary",
        problem_nums=[17, 30, 38, 43, 45, 50, 54, 55, 60, 64, 65, 66, 67, 75, 76, 78, 80, 96, 97, 101, 104, 107, 124, 125, 126, 127, 141, 172, 174, 177, 179, 180, 187, 189, 190, 193, 203],
        num_columns=2,
        landscape=False,
        placement_method="block",
        include_text=True,
        column_spacing_in=3,
        spacing_below_in=1,
        color_to_play="black",
    )

    png_to_pdf(pages, "pages.pdf", page_size, landscape=False)
    #for i, page in enumerate(pages):
    #    page.save(f"page-{i}.png")

    #board_graphic_width_in = 2 + 7/8

    """diagram = make_diagram(
        "cho-elementary",
        533,
        board_graphic_width_in,
    )"""
    

    """
    SYMBOLS = [
        "<",  # empty top-left
        "(",  # empty top
        ")",  # empty bottom
        "!",  # white
        ">",  # empty top-right
        "@",  # black
        "+",  # empty
        "*",  # empty with star point
        " ",  # move to next row
    ]
    """
    
        


if __name__ == "__main__":
    main()