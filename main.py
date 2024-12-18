import random
from PIL import Image, ImageDraw
import reportlab.lib.pagesizes
from draw_game.diagram import *
from create_pdf import png_to_pdf


def create_pages(
    page_size,
    collection,
    margin_in=(0.5, 0.5, 0.5, 0.5),
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
    create_key: bool=True,
    text_rgb: tuple=(128, 128, 128),
    solution_text_rgb: tuple=(128, 128, 128),
    include_page_num: bool=True,
):
    """
    Parameters:
        margin_in: left, top, right, bottom
        color_to_play (str): "default", "black", "white" or "random".
    """
    PAGE_NUM_TEXT_SIZE_IN = 0.125
    PAGE_NUM_RGB = (128, 128, 128)

    if create_key:
        include_text = True

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
    m_l, m_t = margin_in[0] * DPI, margin_in[1] * DPI
    m_r, m_b = margin_in[2] * DPI, margin_in[3] * DPI

    colspan = column_spacing_in * DPI
    spacing_below = spacing_below_in * DPI
    
    col_width_in = (
        w_in - margin_in[0] - margin_in[2] 
        - column_spacing_in*(num_columns-1)
    ) / num_columns
    col_width = col_width_in * DPI

    
        # spacing_below = int(stone_size_px * (int(spacing_below / stone_size_px) + 1))

    col_x = [int(m_l + i*(col_width + colspan)) for i in range(num_columns)]


    # generates diagrams for all the problems and places them in the image.
    if problem_nums is None:
        problem_nums = [i for i in range(1, len(get_problems()[collection]) + 1)]

    pages = []
    key_pages = []
    
    current_col = 0
    current_y = m_t

    if include_page_num:
        page_num = create_text_image(
            str(len(pages) + 1), PAGE_NUM_RGB, PAGE_NUM_TEXT_SIZE_IN
        )
        m_b += page_num.size[1]

    page = Image.new("RGB", (int(w), int(h)), (255, 255, 255))
    key_page = Image.new("RGB", (int(w), int(h)), (255, 255, 255)) if create_key else None

    if include_page_num:
        page_num = create_text_image(
            str(len(pages) + 1), PAGE_NUM_RGB, PAGE_NUM_TEXT_SIZE_IN
        )
        print_x = int(page.size[0]/2 - page_num.size[0]/2)
        print_y = int(h - m_b)
        page.paste(page_num, (print_x, print_y))
        if create_key:
            key_page.paste(page_num, (print_x, print_y))

    for problem_num in problem_nums:
        # determines how this puzzle will be randomly flipped.
        flip_xy = random.choice([True, False]) if random_flip_xy else False
        flip_x = random.choice([True, False]) if random_flip_x else False
        flip_y = random.choice([True, False]) if random_flip_y else False

        #solution_values = [False, True] if show_solution else [False]
        #for show_solution in solution_values:
        diagram = make_diagram(
            collection,
            problem_num,
            col_width_in,
            color_to_play=color_to_play,
            flip_xy=flip_xy,
            flip_x=flip_x,
            flip_y=flip_y,
            placement_method=placement_method,
            include_text=include_text,
            create_key=False,
            text_rgb=text_rgb,
        )

        if create_key:
            key_diagram = make_diagram(
                collection,
                problem_num,
                col_width_in,
                color_to_play=color_to_play,
                flip_xy=flip_xy,
                flip_x=flip_x,
                flip_y=flip_y,
                placement_method=placement_method,
                include_text=include_text,
                create_key=True,
                text_rgb=solution_text_rgb,
            )
        else:
            key_diagram = None


        next_y = current_y + diagram.size[1]
        if next_y > h - m_b:
            current_col += 1
            current_y = m_t

            if current_col >= num_columns:
                # TODO: add image to .pdf
                pages.append(page)
                if create_key:
                    key_pages.append(key_page)
                # ---
                # next page
                page = Image.new("RGB", (int(w), int(h)), (255, 255, 255))

                if create_key:
                    key_page = Image.new("RGB", (int(w), int(h)), (255, 255, 255))

                if include_page_num:
                    page_num = create_text_image(
                        str(len(pages) + 1), PAGE_NUM_RGB, PAGE_NUM_TEXT_SIZE_IN
                    )
                    print_x = int(page.size[0]/2 - page_num.size[0]/2)
                    print_y = int(h - m_b)
                    page.paste(page_num, (print_x, print_y))
                    if create_key:
                        key_page.paste(page_num, (print_x, print_y))

                current_col = 0

        if placement_method == "block":
            stone_size_px = calc_stone_size(col_width_in)
            paste_y = int(stone_size_px * (int(current_y / stone_size_px) + 1))
        else:
            paste_y = int(current_y)
        page.paste(diagram, (col_x[current_col], paste_y))
        if create_key:
            key_page.paste(key_diagram, (col_x[current_col], paste_y))
        current_y += diagram.size[1] + spacing_below

    pages.append(page)
    if create_key:
        key_pages.append(key_page)

    return pages, key_pages


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
    my_problems = [17, 30, 38, 43, 45, 50, 54, 55, 60, 64, 65, 66, 67, 75, 76, 78, 80, 96, 97, 101, 104, 107, 124, 125, 126, 127, 141, 172, 174, 177, 179, 180, 187, 189, 190, 193, 203]
    random.shuffle(my_problems)

    pages, key_pages = create_pages(
        page_size,
        "cho-elementary",
        problem_nums=my_problems,
        num_columns=2,
        landscape=False,
        placement_method="block",
        include_text=True,
        column_spacing_in=3,
        spacing_below_in=1,
        color_to_play="black",
        text_rgb=(255, 255, 255),
        solution_text_rgb=(128, 128, 128),
        include_page_num=True,
    )

    png_to_pdf(pages, "pages.pdf", page_size, landscape=False)
    png_to_pdf(key_pages, "solutions.pdf", page_size, landscape=False)
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