import multiprocessing
from functools import partial
from datetime import datetime
import os
import sys
import tempfile
import time
import numpy as np
from PIL import Image, ImageDraw
import reportlab.lib.pagesizes
from tsumego_pdf.draw_game.board_graphics import (
    BOARD_PADDING_PX,
    TEXT_PADDING_TOP_IN,
    TEXT_PADDING_BOTTOM_IN,
    draw_cover,
)
from tsumego_pdf.draw_game.diagram import *
from tsumego_pdf.puzzles.problems_json import GOKYO_SHUMYO_SECTIONS
from .write_pdf import *

_MAX_PROCESSES = 16
_PAGE_NUM_TEXT_SIZE_IN = 1 / 8
_PAGE_NUM_RGB = (128, 128, 128)
_counter = multiprocessing.Value("i", 0)  # "i" means it's an integer.


class DiagramTemplate:
    def __init__(
        self,
        collection_name=None,
        section_name=None,
        problem_num=None,
        flip_x: bool = False,
        flip_y: bool = False,
        flip_xy: bool = False,
        color_to_play: str = "default",
        is_random_color: bool = False,
        ratio_to_flip_xy=4 / 6,
        stone_size_px: int = 32,
        display_width: int = 19,
        include_text: bool = True,
        text_height_in=0.21,
        play_out_solution: bool = False,
    ):
        self.collection_name = collection_name
        self.section_name = section_name
        self.problem_num = problem_num
        self.color_to_play = color_to_play
        self.is_random_color = is_random_color
        self.x = 0
        self.y = 0

        problem = get_problem(
            collection_name,
            section_name,
            problem_num,
            play_out_solution=False, # not needed for this process.
        )
        
        self.lines = problem["lines"]
        width_stones = problem["show-width"]
        height_stones = problem["show-height"]
        self.play_out_solution = play_out_solution

        if ratio_to_flip_xy < 1:
            min_ratio_to_flip_xy = ratio_to_flip_xy
            max_ratio_to_flip_xy = 1 / ratio_to_flip_xy
        else:
            min_ratio_to_flip_xy = 1 / ratio_to_flip_xy
            max_ratio_to_flip_xy = 1

        if (
            min_ratio_to_flip_xy
            <= abs(width_stones / height_stones)
            <= max_ratio_to_flip_xy
        ):
            # the bbox is relatively square, so it won't be visually jarring
            # to let it be flipped diagonally either way.
            pass
        elif width_stones > display_width - 1:
            # if the bbox of the stones goes beyond the display width,
            # then the diagram will forcibly be flipped diagonally
            # in order to fit within the desired display with.
            flip_xy = True
        elif width_stones >= 5:
            # narrow and small puzzles aren't flipped XY
            # because it's too visually jarring.
            flip_xy = False

        self.ratio_to_flip_xy = ratio_to_flip_xy

        width_px = (width_stones + 1) * stone_size_px + BOARD_PADDING_PX * 2
        height_px = (height_stones + 1) * stone_size_px + BOARD_PADDING_PX * 2

        self.flip_x = flip_x
        self.flip_y = flip_y
        self.flip_xy = flip_xy

        if flip_xy:
            placeholder = width_px
            width_px = height_px
            height_px = placeholder

        width_px = display_width * stone_size_px + BOARD_PADDING_PX * 2

        if include_text:
            height_px += int(
                (TEXT_PADDING_TOP_IN + text_height_in + TEXT_PADDING_BOTTOM_IN) * DPI
            )

        self.size = (width_px, height_px)


class PageTemplate:
    def __init__(
        self,
        width: int,
        height: int,
        include_page_num: bool,
        page_num: int,
    ):
        self.width = width
        self.height = height
        self.page_num = page_num
        self.diagrams = []
        self._diagrams_by_col = {}

    def paste(self, diagram_template, pos, col):
        diagram_template.x = pos[0]
        diagram_template.y = pos[1]
        self.diagrams.append(diagram_template)
        if self._diagrams_by_col.get(col) is None:
            self._diagrams_by_col[col] = []
        self._diagrams_by_col[col].append(diagram_template)

    def space_diagrams_apart(self, start_y, end_y, block: bool, stone_size_px):
        for col in self._diagrams_by_col.keys():
            diagrams = self._diagrams_by_col[col]

            if len(diagrams) < 2:
                continue

            total_box_height = np.sum(d.size[1] for d in diagrams)
            col_height = end_y - start_y
            empty_space = col_height - total_box_height
            spacing = empty_space / (len(diagrams) - 1)

            current_y = start_y
            for diagram in diagrams:
                if block:
                    diagram.y = int(
                        stone_size_px * (int(current_y / stone_size_px) + 1)
                    )
                else:
                    diagram.y = int(current_y)
                current_y += diagram.size[1]
                current_y += spacing


def _init_counter(shared_counter):
    global _counter
    _counter = shared_counter


def _render_page(
    page_template,
    num_pages: int,
    start_time,
    create_key: bool,
    play_out_solution: bool,
    diagram_width_in,
    page_width_in,
    page_height_in,
    include_text: bool,
    show_problem_num: bool,
    force_color_to_play: bool,
    draw_sole_solving_stone: bool,
    solution_mark: str,
    text_rgb: tuple,
    text_height_in,
    include_page_num: bool,
    display_width: int,
    write_collection_label: bool,
    outline_thickness_in,
    line_width_in,
    star_point_radius_in,
    ratio_to_flip_xy,
    bottom_margin,
    booklet_center_padding_in,
    verbose,
):
    global _counter
    page = Image.new(
        "RGB", (int(page_width_in * DPI), int(page_height_in * DPI)), (255, 255, 255)
    )

    for diagram_template in page_template.diagrams:
        diagram = make_diagram(
            diagram_width_in,
            problem_num=diagram_template.problem_num,
            collection_name=diagram_template.collection_name,
            section_name=diagram_template.section_name,
            play_out_solution=diagram_template.play_out_solution,
            color_to_play=diagram_template.color_to_play,
            is_random_color=diagram_template.is_random_color,
            flip_xy=diagram_template.flip_xy,
            flip_x=diagram_template.flip_x,
            flip_y=diagram_template.flip_y,
            include_text=include_text,
            show_problem_num=show_problem_num,
            force_color_to_play=force_color_to_play,
            create_key=create_key,
            draw_sole_solving_stone=draw_sole_solving_stone,
            solution_mark=solution_mark,
            text_rgb=text_rgb,
            text_height_in=text_height_in,
            display_width=display_width,
            write_collection_label=write_collection_label,
            outline_thickness_in=outline_thickness_in,
            line_width_in=line_width_in,
            star_point_radius_in=star_point_radius_in,
            ratio_to_flip_xy=ratio_to_flip_xy,
        )

        page.paste(diagram, (diagram_template.x, diagram_template.y))

    if include_page_num:
        page_num = create_text_image(
            str(page_template.page_num), _PAGE_NUM_RGB, _PAGE_NUM_TEXT_SIZE_IN
        )

        offset = -(booklet_center_padding_in * DPI / 2)

        if page_template.page_num % 2 == 0:
            offset *= -1

        print_x = int((page.size[0] + offset) / 2 - page_num.size[0] / 2)
        print_y = int(page.size[1] - bottom_margin)
        page.paste(page_num, (print_x, print_y))

    with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
        temp_path = temp_file.name
    page.save(temp_path)

    with _counter.get_lock():
        _counter.value += 1
        percent_done = (_counter.value + 2) / num_pages
        elapsed = time.time() - start_time
        avg_duration = elapsed / (_counter.value + 1)
        remaining_processes = num_pages - (_counter.value + 1)
        est = remaining_processes * avg_duration
        if verbose:
            progress_bar(percent_done, est, prefix="1) Render")

    return temp_path


def create_pdf(
    problem_selections,
    page_size=reportlab.lib.pagesizes.letter,
    problems_out_path=None,
    solutions_out_path=None,
    margin_in={"left": 0.5, "top": 0.5, "right": 0.5, "bottom": 0.5},
    is_booklet: bool = False,
    num_signatures: int = 1,
    booklet_key_in_printers_spread: bool = False,
    booklet_center_padding_in=0,
    booklet_cover: str = "chinese",
    embed_cover_in_signatures: bool = False,
    color_to_play: str = "black",
    landscape: bool = False,
    num_columns: int = 2,
    column_spacing_in=0.5,
    spacing_below_in=0.5,
    placement_method: str = "block",
    random_flip: bool = True,
    include_text: bool = True,
    show_problem_num: bool = True,
    force_color_to_play: bool = False,
    create_key: bool = True,
    play_out_solution: bool = True,
    draw_sole_solving_stone: bool = False,
    solution_mark: str = "x",
    problem_text_rgb: tuple = (128, 128, 128),
    solution_text_rgb: tuple = (128, 128, 128),
    text_height_in=0.2,
    include_page_num: bool = True,
    display_width: int = 12,
    outline_thickness_in=1 / 96,
    line_width_in=1 / 96,
    star_point_radius_in=1 / 48,
    draw_bbox_around_diagrams: bool = False,
    ratio_to_flip_xy=5 / 6,
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
        is_booklet (bool): if True, the PDF for the tsumego
                                        is formatted to print out
                                        as a double-sided booklet (printer spread).
                                        The PDF of the key will by default
                                        be written for display on the computer (reader spread).
        num_signatures (int): the number of signatures used in a booklet.
                              if more than 1, then separate PDFs will be saved
                              for any PDFs using printer's spread.
        booklet_key_in_printers_spread (bool): if True, the key PDF is
                                               made to be printed out.
        booklet_center_padding_in (num): the added margin in the center of the booklet.
        booklet_cover (str): the cover displayed.
                             - "japanese"
                             - "chinese"
                             - "korean"
                             - "japanese-hollow"
                             - "chinese-hollow"
                             - "korean-hollow"
                             - "blank"
                             - None
        embed_cover_in_signatures (bool): if True, the cover and back page are directly
                                          part of the first/last signatures respectively.
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
        show_problem_num (bool): if True, the problem number will be shown on the worksheet.
                                 the number is always shown on the key no matter what.
        force_color_to_play (bool): if True, the label "black/white to play"
                                    is shown no matter what.
        create_key (bool): if True, a separate PDF with marked answers is created.
        play_out_solution (bool): if True, the puzzle is played out for the key.
        draw_sole_solving_stone (bool): if True, a stone will be drawn
                                        before the solution marker is drawn
                                        on top of the image, but only if the
                                        puzzle has one single solution alone.
        solution_mark (str): the name of the image marker to use:
                             - "x"
                             - "star"
        problem_text_rgb (tuple): the label color used for the problems print-out.
        solution_text_rgb (tuple): the label color used for the solutions print-out.
        text_height_in (num): the height of the label text.
        include_page_num (bool): if True, a page number
                                 is included in both print-outs.
        display_width (int): the amount of stones wide that are displayed.
                             19 will show the entire board width.
                             12 is ideal for Cho Chikun's problems.
        outline_thickness_in (num): the width of the white stone outline in inches.
        line_width_in (num): the width in inches of the board lines.
        star_point_radius_in (num): the radius of the star points in inches.
        draw_bbox_around_diagrams (bool): if True, a thin rectangle will be drawn
                                          around each diagram. this is useful
                                          for creating stand-alone diagrams.
        ratio_to_flip_xy (num): the ratio a puzzle must fall within
                        to have its X/Y axes considered possibly randomly flipped.
                        5/6 assumes the bbox of the puzzle's side lengths have a ratio
                        that falls between 5/6 and 6/5.
        verbose (bool): if True, a progress bar is displayed.
    """
    global _counter
    _counter = multiprocessing.Value("i", 0)

    num_diagrams_made = 0
    total_diagrams = len(problem_selections)
    if not create_key:
        play_out_solution = False

    """
    Step 1) Opens ReportLab to create PDFs.
    """
    start_time = time.time()

    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%d %H%M%S")
    if problems_out_path is None:
        now = datetime.now()
        problems_out_path = f"tsumego {date_time_str}.pdf"

    if create_key and solutions_out_path is None:
        solutions_out_path = f"tsumego {date_time_str} key.pdf"

    if landscape:
        page_size = (max(page_size), min(page_size))
    else:
        page_size = (min(page_size), max(page_size))

    pdf_width, pdf_height = page_size

    """
    Step 2) Retrieves problems.
    """
    pdf_width_in, pdf_height_in = page_size[0] / 72, page_size[1] / 72

    if is_booklet:
        page_width_in = (pdf_width_in - booklet_center_padding_in) / 2
    else:
        page_width_in = pdf_width_in
    page_height_in = pdf_height_in

    w, h = page_width_in * DPI, page_height_in * DPI

    """
    Step 3) Calculates margins and column variables.
    """
    draw_top = True
    if (
        draw_bbox_around_diagrams
        and spacing_below_in < margin_in["top"] + margin_in["bottom"]
    ):
        spacing_below_in = margin_in["top"] + margin_in["bottom"]
        draw_top = num_columns > 1

    m_l, m_t = margin_in["left"] * DPI, margin_in["top"] * DPI
    m_r, m_b = margin_in["right"] * DPI, margin_in["bottom"] * DPI

    colspan = column_spacing_in * DPI
    spacing_below = spacing_below_in * DPI

    col_width_in = (
        page_width_in
        - margin_in["left"]
        - margin_in["right"]
        - column_spacing_in * (num_columns - 1)
    ) / num_columns
    col_width = col_width_in * DPI
    col_x = [int(m_l + i * (col_width + colspan)) for i in range(num_columns)]

    stone_size_px = calc_stone_size(col_width_in, display_width)

    num_pages = 1
    current_col = 0
    current_y = m_t

    """
    Step 4) Creates blank page templates.
    """
    # generates the text image for the page number
    # to determine how much to change bottom margin.
    if include_page_num:
        page_num_img = create_text_image(
            str(num_pages + 1), _PAGE_NUM_RGB, _PAGE_NUM_TEXT_SIZE_IN
        )
        m_b += page_num_img.size[1]

    """
    Step 5) Begins creating diagrams for each problem.
    """
    # determines if more than one collection is being used.
    collection_names = []
    for selection in problem_selections:
        collection_name = selection[1]
        if collection_name not in collection_names:
            collection_names.append(collection_name)

    write_collection_label = len(collection_names) > 1

    page_templates = []
    page = PageTemplate(
        width=int(w),
        height=int(h),
        include_page_num=include_page_num,
        page_num=num_pages,
    )
    num_pages += 1

    for selection in problem_selections:
        if len(selection) == 1 and selection.endswith(".sgf"):
            problem_dict = load_problem_from_sgf(selection)
        else:
            problem_num = selection[0]
            collection_name = selection[1]
            section_name = None if len(selection) <= 2 else selection[2]
            problem_dict = get_problem(
                collection_name, 
                section_name, 
                problem_num,
                latex_str=None,
                play_out_solution=play_out_solution,
            )

        # determines how this puzzle will be randomly flipped.
        flip_xy = random.choice([True, False]) if random_flip else False
        flip_x = random.choice([True, False]) if random_flip else False
        flip_y = random.choice([True, False]) if random_flip else False

        if color_to_play == "random":
            is_random_color = True
            color_selection = random.choice(["black", "white"])
        else:
            is_random_color = False
            color_selection = color_to_play

        diagram_template = DiagramTemplate(
            collection_name,
            section_name,
            problem_num,
            flip_x,
            flip_y,
            flip_xy,
            color_selection,
            is_random_color,
            ratio_to_flip_xy,
            stone_size_px,
            display_width,
            include_text,
            text_height_in,
            play_out_solution,
        )

        """
        Step 6) Places diagrams in the templates.
        """
        next_y = current_y + diagram_template.size[1]

        if "block" in placement_method:
            paste_y = int(stone_size_px * (int(current_y / stone_size_px) + 1))
        else:
            paste_y = int(current_y)
        paste_next_y = paste_y + diagram_template.size[1]

        if paste_next_y > h - m_b:

            # page has been filled.
            current_col += 1
            current_y = m_t

            if current_col >= num_columns:
                if "proportional" in placement_method:
                    use_block = "block" in placement_method
                    page.space_diagrams_apart(m_t, h - m_b, use_block, stone_size_px)

                page_templates.append(page)
                page = PageTemplate(
                    width=int(w),
                    height=int(h),
                    include_page_num=include_page_num,
                    page_num=num_pages,
                )

                num_pages += 1
                current_col = 0

        if "block" in placement_method:
            paste_y = int(stone_size_px * (int(current_y / stone_size_px) + 1))
        else:
            paste_y = int(current_y)

        page.paste(diagram_template, (col_x[current_col], paste_y), current_col)
        current_y += diagram_template.size[1] + spacing_below

    if "proportional" in placement_method:
        use_block = "block" in placement_method
        page.space_diagrams_apart(m_t, h - m_b, use_block, stone_size_px)

    page_templates.append(page)

    """
    Step 7) Render pages from their templates using multiprocessing.
    """
    total_pages_to_print = num_pages * 2 if create_key else num_pages

    page_render_start = time.time()

    prob_temp_paths = []
    key_temp_paths = []

    problem_render_page_partial = partial(
        _render_page,
        num_pages=total_pages_to_print,
        start_time=page_render_start,
        create_key=False,
        play_out_solution=False,
        diagram_width_in=col_width_in,
        page_width_in=page_width_in,
        page_height_in=page_height_in,
        include_text=include_text,
        show_problem_num=show_problem_num,
        force_color_to_play=force_color_to_play,
        draw_sole_solving_stone=draw_sole_solving_stone,
        solution_mark=solution_mark,
        text_rgb=problem_text_rgb,
        text_height_in=text_height_in,
        include_page_num=include_page_num,
        display_width=display_width,
        write_collection_label=write_collection_label,
        outline_thickness_in=outline_thickness_in,
        line_width_in=line_width_in,
        star_point_radius_in=star_point_radius_in,
        ratio_to_flip_xy=ratio_to_flip_xy,
        bottom_margin=m_b,
        booklet_center_padding_in=booklet_center_padding_in,
        verbose=verbose,
    )

    if create_key:
        key_render_page_partial = partial(
            _render_page,
            start_time=page_render_start,
            num_pages=total_pages_to_print,
            create_key=True,
            play_out_solution=play_out_solution,
            diagram_width_in=col_width_in,
            page_width_in=page_width_in,
            page_height_in=page_height_in,
            include_text=include_text,
            show_problem_num=show_problem_num,
            force_color_to_play=force_color_to_play,
            draw_sole_solving_stone=draw_sole_solving_stone,
            solution_mark=solution_mark,
            text_rgb=solution_text_rgb,
            text_height_in=text_height_in,
            include_page_num=include_page_num,
            display_width=display_width,
            write_collection_label=write_collection_label,
            outline_thickness_in=outline_thickness_in,
            line_width_in=line_width_in,
            star_point_radius_in=star_point_radius_in,
            ratio_to_flip_xy=ratio_to_flip_xy,
            bottom_margin=m_b,
            booklet_center_padding_in=booklet_center_padding_in,
            verbose=verbose,
        )

        with (
            multiprocessing.Pool(
                processes=_MAX_PROCESSES,
                initializer=_init_counter,
                initargs=(_counter,),
            ) as pool_a,
            multiprocessing.Pool(
                processes=_MAX_PROCESSES,
                initializer=_init_counter,
                initargs=(_counter,),
            ) as pool_b,
        ):
            # maps the partial function to the list of PageTemplate objects.
            prob_temp_paths = pool_a.map(problem_render_page_partial, page_templates)
            key_temp_paths = pool_b.map(key_render_page_partial, page_templates)
    else:
        with multiprocessing.Pool(
            processes=_MAX_PROCESSES,
            initializer=_init_counter,
            initargs=(_counter,),
        ) as pool:
            # maps the partial function to the list of PageTemplate objects.
            prob_temp_paths = pool.map(problem_render_page_partial, page_templates)

    if verbose:
        sys.stdout.write("\r" + " " * 80)
        sys.stdout.flush()
        sys.stdout.write("\r")

    """
    Step 8) The temporary images are used to create the PDFs.
    """
    prob_process = None
    key_process = None
    if is_booklet:
        prob_process = multiprocessing.Process(
            target=write_images_to_booklet_pdf,
            args=(
                prob_temp_paths,
                problems_out_path,
                page_size,
                booklet_center_padding_in,
                True,
                booklet_cover,
                embed_cover_in_signatures,
                num_signatures,
                verbose and not create_key,  # not verbose if key is.
            ),
        )

        if create_key:
            key_process = multiprocessing.Process(
                target=write_images_to_booklet_pdf,
                args=(
                    key_temp_paths,
                    solutions_out_path,
                    page_size,
                    booklet_center_padding_in,
                    booklet_key_in_printers_spread,
                    booklet_cover,
                    embed_cover_in_signatures,
                    num_signatures,
                    verbose,  # verbose.
                ),
            )

    else:
        prob_process = multiprocessing.Process(
            target=write_images_to_pdf,
            args=(
                prob_temp_paths,
                problems_out_path,
                page_size,
                not create_key,  # not verbose if key is.
            ),
        )

        if create_key:
            key_process = multiprocessing.Process(
                target=write_images_to_pdf,
                args=(
                    key_temp_paths,
                    solutions_out_path,
                    page_size,
                    True,  # verbose.
                ),
            )

    if key_process is not None:
        prob_process.start()
        key_process.start()
        prob_process.join()
        key_process.join()
    else:
        prob_process.start()
        prob_process.join()

    """
    Step 9) Deletes resources and prints out a conclusive message.
    """
    for path in prob_temp_paths:
        os.remove(path)

    for path in key_temp_paths:
        os.remove(path)

    sys.stdout.write("\r" + " " * 80)
    sys.stdout.flush()
    sys.stdout.write("\r")

    if verbose:
        if create_key:
            print(
                "A collection of tsumego and its key have been saved to "
                f'"{problems_out_path}" and "{solutions_out_path}".\n'
            )
        else:
            print(
                "A collection of tsumego has been " f'saved to "{problems_out_path}".\n'
            )
