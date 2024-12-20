from datetime import datetime
import os
import sys
import tempfile
import time
from PIL import Image, ImageDraw
import reportlab.lib.pagesizes
from reportlab.pdfgen import canvas
from tsumego_pdf.draw_game.diagram import *
from tsumego_pdf.puzzles.problems_json import GOKYO_SHUMYO_SECTIONS


def _progress_bar(
    percent_done,
    est_seconds_left=None,
    length=50,
    fill="█",
    print_end="\r",
):
    """
    Prints a progress bar to the console.

    Parameters:
        total (int): total iterations or steps.
        est_seconds_left: the amount of seconds estimated to remain.
        length (int): length of the progress bar.
        fill (str): character to fill the progress bar.
        print_end (str): ending character (default is a carriage return).
    """
    if est_seconds_left is None:
        prefix = "        "
    else:
        seconds = round(est_seconds_left)
        minutes = seconds // 60
        hours = minutes // 60

        seconds = seconds % 60
        minutes = minutes % 60
        prefix = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    filled_length = int(length * percent_done) if percent_done != 0 else 0
    bar = fill * filled_length + "-" * (length - filled_length)
    sys.stdout.write(f"\r{prefix} |{bar}| {percent_done*100:.1f}%")
    sys.stdout.flush()
    sys.stdout.write(print_end)


def create_pdf(
    problem_selections,
    page_size=reportlab.lib.pagesizes.letter,
    problems_out_path=None,
    solutions_out_path=None,
    margin_in={"left": 0.5, "top": 0.5, "right": 0.5, "bottom": 0.5},
    color_to_play: str = "black",
    landscape: bool = False,
    num_columns: int = 2,
    column_spacing_in=0.5,
    spacing_below_in=0.5,
    placement_method: str = "block",
    random_flip: bool = True,
    include_text: bool = True,
    create_key: bool = True,
    problem_text_rgb: tuple = (128, 128, 128),
    solution_text_rgb: tuple = (128, 128, 128),
    text_height_in=0.2,
    include_page_num: bool = True,
    display_width: int = 12,
    verbose: bool = True,
):
    """
    Parameters:
        problem_selections (list):
            a list of problems to select.
            each element will be a tuple,
            where the first element is the problem number,
            and the second element is the collection name.
            if you're selecting from the Gokyo Shumyo, the third element
            will be the section name.

            the name of the collection to select problems from are:
            - "cho-elementary": the fundamentals
                                (900 problems).
            - "cho-intermediate": builds upon principles of Life & Death
                                  (861 problems).
            - "cho-advanced": Life & Death problems for well-versed players
                              (792 problems).
            - "gokyo-shumyo": A famous 1812 collection
                              from Japan for well-versed players.
                              It contains the following sections:
                                  "living": Making living groups (103 problems).
                                  "killing": Killing stone groups (71 problems).
                                  "ko": Creating a Ko (90 problems).
                                  "capturing-race": Counting liberties
                                                    (96 problems).
                                  "oiotoshi": Connect-and-die (40 problems).
                                  "connecting": Watari (74 problems).
                                  "various": Wedges, Connects, Cuts,
                                             Ladders, etc. (46 problems).
            - "xuanxuan-qijing": A famous 1349 collection from China.
                                 Quite difficult. (347 problems).
            - "igo-hatsuyoron": A famous 1713 collection from Japan
                                which contains some of the hardest puzzles
                                ever conceived (183 problems).
        page_size (tuple): a page size from ReportLab. 72 pixels per inch.
        problems_out_path: the .pdf path for the output.
                           If None, the function will figure out some name.
        solutions_out_path: the .pdf path for the output.
                            If None, the function will figure out some name.
        margin_in (dict): the print margin for each side of the page in inches.
        color_to_play (str): "default", "black", "white" or "random".
        landscape (bool): if True, the paper is oriented landscape.
        num_columns (int): the number of columns used to print puzzles.
        column_spacing_in (num): the distance in inches between columns.
        spacing_below_in (num): the distance below each puzzle in inches.
        placement_method (str): the way puzzles are placed:
            - "default" places puzzles without care.
            - "block" places puzzles so their grid lines line up.
        random_flip (bool): if True, the puzzle can be randomly flipped around.
        include_text (bool): if True, a label is included below the diagram.
        create_key (bool): if True, a separate PDF with marked answers is created.
        problem_text_rgb (tuple): the label color used for the problems print-out.
        solution_text_rgb (tuple): the label color used for the solutions print-out.
        text_height_in (num): the height of the label text.
        include_page_num (bool): if True, a page number
                                 is included in both print-outs.
        display_width (int): the amount of stones wide that are displayed.
                             19 will show the entire board width.
                             12 is ideal for Cho Chikun's problems.
        verbose (bool): if True, a progress bar is displayed.
    """
    PAGE_NUM_TEXT_SIZE_IN = 0.125
    PAGE_NUM_RGB = (128, 128, 128)

    num_diagrams_made = 0
    total_diagrams = len(problem_selections)

    """
    Step 1) Opens ReportLab to create PDFs.
    """
    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    if problems_out_path is None:
        now = datetime.now()
        problems_out_path = f"{date_time_str} tsumego problems.pdf"

    if create_key:
        include_text = True
        if solutions_out_path is None:
            problems_out_path = f"{date_time_str} tsumego solutions.pdf"

    if landscape:
        page_size = (max(page_size), min(page_size))
    else:
        page_size = (min(page_size), max(page_size))

    prob_pdf = canvas.Canvas(problems_out_path, pagesize=page_size)
    if create_key:
        solve_pdf = canvas.Canvas(solutions_out_path, pagesize=page_size)

    pdf_width, pdf_height = page_size

    """
    Step 2) Ensures problems.
    """
    problems = get_problems()
    """if problems.get(collection_name) is None:
        print(
            f"'{collection_name}'' is not an available collection."
            "Only the following are accepted:"
        )
        for key in problems.keys():
            print(f'\t- "{key}"')

        return"""

    w_in, h_in = page_size[0] / 72, page_size[1] / 72
    if landscape and w_in < h_in:
        placeholder = w_in
        w_in = h_in
        h_in = placeholder
    w, h = w_in * DPI, h_in * DPI

    """
    Step 3) Calculates margins and column variables.
    """
    m_l, m_t = margin_in["left"] * DPI, margin_in["top"] * DPI
    m_r, m_b = margin_in["right"] * DPI, margin_in["bottom"] * DPI

    colspan = column_spacing_in * DPI
    spacing_below = spacing_below_in * DPI

    col_width_in = (
        w_in
        - margin_in["left"]
        - margin_in["right"]
        - column_spacing_in * (num_columns - 1)
    ) / num_columns
    col_width = col_width_in * DPI
    col_x = [int(m_l + i * (col_width + colspan)) for i in range(num_columns)]

    num_pages = 0
    current_col = 0
    current_y = m_t

    # generates the text image for the page number.
    if include_page_num:
        page_num = create_text_image(
            str(num_pages + 1), PAGE_NUM_RGB, PAGE_NUM_TEXT_SIZE_IN
        )
        m_b += page_num.size[1]

    page = Image.new("RGB", (int(w), int(h)), (255, 255, 255))
    key_page = (
        Image.new("RGB", (int(w), int(h)), (255, 255, 255)) if create_key else None
    )

    if include_page_num:
        # adds page number.
        page_num = create_text_image(
            str(num_pages + 1), PAGE_NUM_RGB, PAGE_NUM_TEXT_SIZE_IN
        )
        print_x = int(page.size[0] / 2 - page_num.size[0] / 2)
        print_y = int(h - m_b)
        page.paste(page_num, (print_x, print_y))
        if create_key:
            key_page.paste(page_num, (print_x, print_y))

    temp_paths = []

    def write_page_to_pdf(page, pdf, show_page: bool = True):
        with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
            temp_path = temp_file.name
        page.save(temp_path)
        temp_paths.append(temp_path)

        img_w, img_h = page.size
        scale_x = pdf_width / img_w
        scale_y = pdf_height / img_h
        scale = min(scale_x, scale_y)

        pdf.drawImage(
            temp_path,
            0,
            0,
            width=img_w * scale,
            height=img_h * scale,
        )
        if show_page:
            pdf.showPage()

    # determines if more than one collection is being used.
    collection_names = []
    for selection in problem_selections:
        collection_name = selection[1]
        if collection_name not in collection_names:
            collection_names.append(collection_name)

    start_time = time.time()
    longest_first_time = 0

    for selection in problem_selections:
        problem_num = selection[0]
        collection_name = selection[1]
        section_name = None if len(selection) <= 2 else selection[2]

        # determines how this puzzle will be randomly flipped.
        flip_xy = random.choice([True, False]) if random_flip else False
        flip_x = random.choice([True, False]) if random_flip else False
        flip_y = random.choice([True, False]) if random_flip else False

        # solution_values = [False, True] if show_solution else [False]
        # for show_solution in solution_values:
        diagram = make_diagram(
            col_width_in,
            problem_num,
            collection_name,
            section_name,
            color_to_play=color_to_play,
            flip_xy=flip_xy,
            flip_x=flip_x,
            flip_y=flip_y,
            include_text=include_text,
            create_key=False,
            text_rgb=problem_text_rgb,
            text_height_in=text_height_in,
            display_width=display_width,
            write_collection_label=len(collection_names) > 1,
        )

        if create_key:
            key_diagram = make_diagram(
                col_width_in,
                problem_num,
                collection_name,
                section_name,
                color_to_play=color_to_play,
                flip_xy=flip_xy,
                flip_x=flip_x,
                flip_y=flip_y,
                include_text=include_text,
                create_key=True,
                text_rgb=solution_text_rgb,
                text_height_in=text_height_in,
                display_width=display_width,
                write_collection_label=len(collection_names) > 1,
            )
        else:
            key_diagram = None

        num_diagrams_made += 1

        if verbose:
            elapsed = time.time() - start_time
            avg_diagram_time = elapsed / num_diagrams_made
            num_remaining = total_diagrams - num_diagrams_made
            est_seconds_left = num_remaining * avg_diagram_time

            percent_done = num_diagrams_made / total_diagrams
            if percent_done < 0.1:
                est_seconds_left = None

            _progress_bar(percent_done, est_seconds_left)

        next_y = current_y + diagram.size[1]
        if next_y > h - m_b:
            # page has been filled.
            current_col += 1
            current_y = m_t

            if current_col >= num_columns:
                write_page_to_pdf(page, prob_pdf)

                if create_key:
                    write_page_to_pdf(key_page, solve_pdf)

                num_pages += 1

                # creates a new blank page.
                page = Image.new("RGB", (int(w), int(h)), (255, 255, 255))
                if create_key:
                    key_page = Image.new("RGB", (int(w), int(h)), (255, 255, 255))

                if include_page_num:
                    page_num = create_text_image(
                        str(num_pages + 1), PAGE_NUM_RGB, PAGE_NUM_TEXT_SIZE_IN
                    )
                    print_x = int(page.size[0] / 2 - page_num.size[0] / 2)
                    print_y = int(h - m_b)
                    page.paste(page_num, (print_x, print_y))
                    if create_key:
                        key_page.paste(page_num, (print_x, print_y))

                current_col = 0

        if placement_method == "block":
            stone_size_px = calc_stone_size(col_width_in, display_width)
            paste_y = int(stone_size_px * (int(current_y / stone_size_px) + 1))
        else:
            paste_y = int(current_y)
        page.paste(diagram, (col_x[current_col], paste_y))
        if create_key:
            key_page.paste(key_diagram, (col_x[current_col], paste_y))
        current_y += diagram.size[1] + spacing_below

    write_page_to_pdf(page, prob_pdf, show_page=False)
    prob_pdf.save()

    if create_key:
        write_page_to_pdf(key_page, solve_pdf, show_page=False)
        solve_pdf.save()

    # deletes page images now that the PDFs are complete.
    for path in temp_paths:
        os.remove(path)

    sys.stdout.write(f"\r" + " " * 70)
    sys.stdout.flush()
    sys.stdout.write("\r")
    if verbose:
        if create_key:
            print(
                "A collection of tsumego and its key have been saved to "
                f"{problems_out_path} and {solutions_out_path}.\n"
            )
        else:
            print(f"Tsumego has been saved to {problems_out_path}.\n")
