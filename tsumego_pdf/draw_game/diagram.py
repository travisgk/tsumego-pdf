"""
tsumego_pdf.draw_game.diagram.py
---
This file contains functionality to draw a tsumego diagram
with or without the solution(s) marked.
"""

import json
import os
import random
from PIL import Image, ImageDraw
from tsumego_pdf.puzzles.problems_json import (
    GOKYO_SHUMYO_SECTIONS,
    get_problem,
)
from tsumego_pdf.puzzles.playout import BLACK_STONES, WHITE_STONES
from .board_graphics import *


def calc_stone_size(diagram_width_in, display_width):
    """
    Returns the size of a stone graphic in pixels
    for the given diagram width and the span of the stones displayed.
    """
    cells_wide = min(19, display_width)
    stone_size_in = diagram_width_in / cells_wide
    stone_size_px = stone_size_in * DPI

    return int(stone_size_px)


def make_diagram(
    diagram_width_in,
    problem_num: int = None,
    collection_name: str = None,
    section_name: str = None,
    latex_str: str = None,
    color_to_play: str = "default",
    is_random_color: bool = False,
    flip_xy: bool = True,
    flip_x: bool = True,
    flip_y: bool = True,
    include_text: bool = True,
    show_problem_num: bool = True,
    force_color_to_play: bool = False,
    create_key: bool = True,
    play_out_solution: bool = False,
    draw_sole_solving_stone: bool = False,
    solution_mark: str = "x",
    text_rgb: tuple = (127, 127, 127),
    text_height_in=0.2,
    display_width: int = 12,
    write_collection_label: bool = False,
    outline_thickness_in=1 / 128,
    line_width_in=1 / 96,
    star_point_radius_in=None,
    ratio_to_flip_xy=5 / 6,
):
    """
    Returns a PIL Image of a Life and Death diagram for the desired problem.

    Parameters:
        diagram_width_in (num): the output diagram width in inches.
        problem_num (int): the problem number.
        collection_name (str): the name of the collection to use.
            - "cho-elementary"
            - "cho-intermediate"
            - "cho-advanced"
            - "gokyo-shumyo"
            - "xuanxuan-qijing"
            - "igo-hatsuyoron"
        section_name (str): the name of the section to use.
                            for any collection other than the Gokyo Shumyo
                            this will be None.
        latex_str (str): overrides the problem selection process and just
                         makes a diagram of the LaTeX given directly.
                         None by default.
        color_to_play (str):
            - "default": keeps stone colors as they are in the original data.
            - "black": forces the player to move to be black.
            - "white": forces the player to move to be white.
            - "random": forces the player to move to be random.
        is_random_color (bool): True if the color was gotten through randomization.
                                Don't worry about this if color_to_play is "random".
        flip_xy (bool): if True, problem has its X/Y axes flipped.
        flip_x (bool): if True, problem is flipped across X-axis.
        flip_y (bool): if True, problem is flipped across Y-axis.
        include_text (bool): if True, a problem label
                             will be added to the diagram.
        show_problem_num (bool): if True, the problem number will be shown on the worksheet.
                                 the number is always shown on the key no matter what.
        force_color_to_play (bool): if True, the label "black/white to play"
                                    is shown no matter what.
        create_key (bool): if True, the problem solution(s) is/are marked.
        draw_sole_solving_stone (bool): if True, a stone will be drawn
                                        before the solution marker is drawn
                                        on top of the image, but only if the
                                        puzzle has one single solution alone.
        solution_mark (str): the name of the image marker to use:
                             - "x"
                             - "star"
        text_rgb (tuple): the RGB for the label below the diagram.
        text_height_in (num): the height of the label text.
        display_width (int): the maximum width of the board displayed.
                             12 is a good value for Cho's problems.
        write_collection_label (bool): if True, the collection name is shown.
        line_width_in (num): the width in inches of the board lines.
        star_point_radius_in (num): the radius of the star points in inches.
        ratio_to_flip_xy (num): the ratio a puzzle must fall within
                                to have its X/Y axes considered possibly randomly flipped.
                                5/6 assumes the bbox of the puzzle's side lengths have a ratio
                                that falls between 5/6 and 6/5.
    """

    """
    Step 1) Setup.
    """
    # determine the stone size.
    stone_size_px = calc_stone_size(diagram_width_in, display_width)
    refresh_stone_graphics(stone_size_px, solution_mark, outline_thickness_in)

    # determines color to play.
    if color_to_play == "random":
        is_random_color = True
        color_to_play = random.choice(["black", "white"])

    # draws a full board.
    full_board_width_in = ((stone_size_px * 19) - BOARD_PADDING_PX * 2) / DPI
    board, board_draw = draw_board(
        stone_size_px=stone_size_px,
        line_width_in=line_width_in,
        star_point_radius_in=star_point_radius_in,
    )

    if ratio_to_flip_xy < 1:
        min_ratio_to_flip_xy = ratio_to_flip_xy
        max_ratio_to_flip_xy = 1 / ratio_to_flip_xy
    else:
        min_ratio_to_flip_xy = 1 / ratio_to_flip_xy
        max_ratio_to_flip_xy = ratio_to_flip_xy

    """
    Step 2) Get problem info.
    """
    if not create_key:
        play_out_solution = False

    problem_dict = get_problem(
        collection_name,
        section_name,
        problem_num,
        latex_str,
        play_out_solution=play_out_solution,
    )
    lines = problem_dict["lines"]
    default_to_play = problem_dict["default-to-play"]
    max_x = problem_dict["show-width"] - 1
    max_y = problem_dict["show-height"] - 1

    """
    Step 3) Draws stones and determines the bounding box of the stones.
    """
    invert_colors = color_to_play != "default" and default_to_play != color_to_play
    NUM_CHARS = "123456789" + BLACK_STONES[1:] + WHITE_STONES[1:]

    marks = []
    solution_nums = []
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            if c in BLACK_STONES:  # black stone.
                draw_stone(
                    board,
                    x,
                    y,
                    stone_size_px,
                    is_black=not invert_colors,
                    outline_thickness_in=outline_thickness_in,
                )
            elif c in WHITE_STONES:  # white stone.
                draw_stone(
                    board,
                    x,
                    y,
                    stone_size_px,
                    is_black=invert_colors,
                    outline_thickness_in=outline_thickness_in,
                )
            elif create_key and c == "X":  # solution.
                marks.append((x, y))

            if create_key:
                if c not in "!@+" and c in NUM_CHARS:
                    solution_nums.append(((x, y), c))

    if max_x == 0:
        max_x = 18
    if max_y == 0:
        max_y = 18

    """
    Step 4) Adjusts the bounding box to crop out the puzzle while also
            leaning more toward keeping diagrams ideal for horizontal display.
    """

    # flips the puzzle randomly.
    if flip_xy:
        board = board.transpose(Image.TRANSPOSE)
    if flip_x:
        board = board.transpose(Image.FLIP_TOP_BOTTOM)
    if flip_y:
        board = board.transpose(Image.FLIP_LEFT_RIGHT)

    # simulates the reflections to determine where to crop the image.
    # the solution marks are reflected here as well and
    # then ultimately drawn.
    is_top = True
    is_left = True
    if flip_xy:
        placeholder = is_top
        is_top = is_left
        is_left = placeholder

        placeholder = max_x
        max_x = max_y
        max_y = placeholder

        marks = [(y, x) for x, y in marks]
        solution_nums = [((p[1], p[0]), c) for p, c in solution_nums]

    if flip_x:
        is_top = not is_top
        marks = [(x, 18 - y) for x, y in marks]
        solution_nums = [((p[0], 18 - p[1]), c) for p, c in solution_nums]

    if flip_y:
        is_left = not is_left
        marks = [(18 - x, y) for x, y in marks]
        solution_nums = [((18 - p[0], p[1]), c) for p, c in solution_nums]

    # counts the number of solutions this problem has.
    num_solutions = 0
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            if c == "X":
                num_solutions += 1

    is_black = color_to_play == "black" or (
        color_to_play == "default" and default_to_play == "black"
    )
    mark_is_black = (is_black and not invert_colors) or (not is_black and invert_colors)
    for x, y in marks:
        if draw_sole_solving_stone and num_solutions == 1:
            draw_stone(
                board,
                x,
                y,
                stone_size_px,
                is_black=is_black,
                outline_thickness_in=outline_thickness_in,
            )

        black_mark = (
            not mark_is_black
            if draw_sole_solving_stone and len(marks) == 1
            else mark_is_black
        )

        draw_mark(board, x, y, stone_size_px, is_black=black_mark)

    for point, char in solution_nums:
        x, y = point
        draw_key_number(
            board,
            x,
            y,
            stone_size_px,
            char,
        )

    # crops the puzzle.
    w, h = board.size
    OFF = BOARD_PADDING_PX
    left = 0 if is_left else max(0, w - stone_size_px * display_width - OFF)
    right = min(w - 1, left + stone_size_px * display_width + OFF)
    top = 0 if is_top else max(0, h - stone_size_px * (max_y + 2) - OFF)
    bottom = min(h - 1, top + stone_size_px * (max_y + 2) + OFF)

    if abs(bottom - top) >= 15 * stone_size_px:
        # the height isn't cropped
        # if stones are already taking up most of the board.
        top = 0
        bottom = h - 1

    if not (left <= 0 and top <= 0 and bottom >= h - 1 and right >= w - 1):
        board = board.crop((left, top, right, bottom))

    """
    Step 5) Creates the image text for below the diagram.
    """
    if include_text:
        # determines if the color to play should be displayed.
        MULTICOLOR_COLLECTIONS = ["gokyo-shumyo", "xuanxuan-qijing", "igo-hatsuyoron"]

        state_color_to_play = (
            force_color_to_play
            or is_random_color
            or (
                color_to_play == "default"
                and any(term in collection_name for term in MULTICOLOR_COLLECTIONS)
            )
        )

        # the text to be displayed is determined.
        text_str = ""
        if create_key or show_problem_num:
            if "gokyo-shumyo" in collection_name:
                reverse_dict = {
                    value: key for key, value in GOKYO_SHUMYO_SECTIONS.items()
                }
                section_num = reverse_dict[section_name]
                text_str = f"problem {section_num}-{problem_num}"
            else:
                text_str = f"problem {problem_num}"

        if state_color_to_play:
            if color_to_play == "default":
                color_str = default_to_play
            else:
                color_str = color_to_play

            if create_key or show_problem_num:
                text_str += f", {color_to_play} to play"
            else:
                text_str = f"{color_to_play} to play"

        label_str = None
        if write_collection_label:
            LABELS = {
                "cho-elementary": "Cho's Elementary",
                "cho-intermediate": "Cho's Intermediate",
                "cho-advanced": "Cho's Advanced",
                "gokyo-shumyo": "Gokyo Shumyo",
                "xuanxuan-qijing": "Xuanxuan Qijing",
                "igo-hatsuyoron": "Igo Hatsuyōron",
            }
            label_str = LABELS[collection_name]

        TEXT_PADDING_TOP = TEXT_PADDING_TOP_IN * DPI
        TEXT_PADDING_BOTTOM = TEXT_PADDING_BOTTOM_IN * DPI

        if label_str is None:
            label_image = None
            text_image = create_text_image(text_str, text_rgb, text_height_in)
            additional_height = int(
                text_image.size[1] + TEXT_PADDING_TOP + TEXT_PADDING_BOTTOM
            )
        else:
            label_image = create_text_image(label_str, text_rgb, text_height_in / 2)
            text_image = create_text_image(text_str, text_rgb, text_height_in / 2)
            additional_height = int(
                label_image.size[1]
                + text_image.size[1]
                + TEXT_PADDING_TOP
                + TEXT_PADDING_BOTTOM
            )

        """
        Step 6) Combines the diagram and label as one image.
        """
        w, h = board.size
        new_image = Image.new("RGB", (w, h + additional_height), (255, 255, 255))
        new_image.paste(board, (0, 0))

        if label_str is None:
            text_x = int(w / 2 - text_image.size[0] / 2)
            new_image.paste(text_image, (text_x, int(h + TEXT_PADDING_TOP)))
        else:
            label_x = int(w / 2 - label_image.size[0] / 2)
            new_image.paste(label_image, (label_x, int(h + TEXT_PADDING_TOP)))

            text_x = int(w / 2 - text_image.size[0] / 2)
            new_image.paste(
                text_image, (text_x, int(h + TEXT_PADDING_TOP + label_image.size[1]))
            )

        board = new_image

    return board
