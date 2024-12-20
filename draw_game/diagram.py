import json
import os
import random
from PIL import Image, ImageDraw
from puzzles.problems_json import GOKYO_SHUMYO_SECTIONS, create_problems_json
from .board_graphics import *

_PROBLEMS = None


def get_problems():
    """Returns a dictionary containing all the Go problems."""
    _load_problems()
    return _PROBLEMS


def _load_problems():
    """Loads all the problems to memory if not done yet."""
    global _PROBLEMS
    if _PROBLEMS is not None:
        return

    local_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(local_dir, "puzzles", "go-problems.json")

    if not os.path.exists(file_path):
        create_problems_json(file_path)

    with open(file_path, "r") as file:
        _PROBLEMS = json.load(file)


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
    collection: str,
    problem_num,
    diagram_width_in,
    color_to_play: str = "default",
    flip_xy: bool = True,
    flip_x: bool = True,
    flip_y: bool = True,
    include_text: bool = True,
    placement_method: str = "block",
    force_color_to_play: bool = False,
    create_key: bool = False,
    text_rgb: tuple = (128, 128, 128),
    text_height_in=0.2,
    display_width: int = 12,
):
    """
    Returns a PIL Image of a Life and Death diagram for the desired problem.

    Parameters:
        collection (str): the name of the collection to use.
            - "cho-elementary"
            - "cho-intermediate"
            - "cho-advanced"
            - "gokyo-shumyo"
            - "xuanxuan-qijing"
            - "igo-hatsuyoron"
        problem_num: the problem number (int),
                     or a tuple with the problem number
                     and the section name (tuple(int, str)).
        diagram_width_in (num): the output diagram width in inches.
        color_to_play (str):
            - "default": keeps stone colors as they are in the original data.
            - "black": forces the player to move to be black.
            - "white": forces the player to move to be white.
            - "random": forces the player to move to be random.
        flip_xy (bool): if True, problem has its X/Y axes flipped.
        flip_x (bool): if True, problem is flipped across X-axis.
        flip_y (bool): if True, problem is flipped across Y-axis.
        include_text (bool): if True, a problem label
                             will be added to the diagram.
        force_color_to_play (bool): if True, the label "black/white to play"
                                    is shown no matter what.
        create_key (bool): if True, the problem solution(s) is/are marked.
        text_rgb (tuple): the RGB for the label below the diagram.
        text_height_in (num): the height of the label text.
        display_width (int): the maximum width of the board displayed.
                             12 is a good value for Cho's problems.
    """

    """
    Step 1) Setup.
    """
    # determine the stone size.
    stone_size_px = calc_stone_size(diagram_width_in, display_width)

    # determines color to play.
    random_color = False
    if color_to_play == "random":
        random_color = True
        color_to_play = random.choice(["black", "white"])

    # draws a full board.
    full_board_width_in = (stone_size_px * 19) / DPI
    board, board_draw = draw_board(width_in=full_board_width_in)

    """
    Step 2) Problem retrieval.
    """
    # loads the problems if not yet done, then selects the problem.
    _load_problems()

    collection = collection.lower()
    problem_collection = _PROBLEMS.get(collection)
    if problem_collection is None:
        print(
            f"'{collection}'' is not an available collection. "
            "Only the following are accepted:"
        )
        for key in _PROBLEMS.keys():
            print(f'\t- "{key}"')

        return None

    section_name = None
    if "gokyo-shumyo" in collection:
        # the section name must be considered.
        problem_num, section_name = problem_num
        section = problem_collection.get(section_name)
        if section is None:
            print(
                f"The collection '{collection}' does not have "
                f"a section named {section_name}."
            )
            return None

        lines = section.get(str(problem_num))
        if lines is None:
            print(
                f"The section '{section_name}' of {collection} "
                f"does not have a problem numbered #{problem_num}."
            )
            return None

    else:
        lines = problem_collection.get(str(problem_num))
        if lines is None:
            print(
                f"The collection '{collection}' does not have "
                f"a problem numbered #{problem_num}."
            )
            return None

    lines = lines.split(" ")
    default_to_play = "black" if lines[0][0] == "B" else "white"
    lines[0] = lines[0][1:]

    """
    Step 3) Draws stones and determines the bounding box of the stones.
    """
    max_x, max_y = 0, 0

    invert_colors = color_to_play != "default" and default_to_play != color_to_play

    marks = []
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            if c == "@":  # black stone.
                draw_stone(board, x, y, stone_size_px, is_black=not invert_colors)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
            elif c == "!":  # white stone.
                draw_stone(board, x, y, stone_size_px, is_black=invert_colors)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
            elif create_key and c == "X":  # solution.
                marks.append((x, y))

    """
    Step 4) Adjusts the bounding box to crop out the puzzle while also
            leaning more toward keeping diagrams ideal for horizontal display.
    """
    # flipping the X and Y axes is forbidden/enforced depending on
    # the bbox attributes.
    if 0.9 < abs(max_x / max_y) < 1.1:
        # the bbox is relatively square, so it won't be visually jarring
        # to let it be flipped diagonally either way.
        pass
    elif max_x > display_width - 2:
        # if the bbox of the stones goes beyond the display width,
        # then the diagram will forcibly be flipped diagonally
        # in order to fit within the desired display with.
        flip_xy = True
    elif max_x >= 4:
        # narrow and small puzzles aren't flipped XY
        # because it's too visually jarring.
        flip_xy = False

    # flips the puzzle aint randomly.
    if flip_xy:
        board = board.transpose(Image.TRANSPOSE)
    if flip_x:
        board = board.transpose(Image.FLIP_TOP_BOTTOM)
    if flip_y:
        board = board.transpose(Image.FLIP_LEFT_RIGHT)

    # simulates the reflections to determine where to crop the image.
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

    if flip_x:
        is_top = not is_top
        marks = [(x, 18 - y) for x, y in marks]

    if flip_y:
        is_left = not is_left
        marks = [(18 - x, y) for x, y in marks]

    for x, y in marks:
        draw_mark(board, x, y, stone_size_px, is_black=not invert_colors)

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
        bottom = h

    board = board.crop((left, top, right, bottom))

    """
    Step 5) Creates the image text for below the diagram.
    """
    if include_text:
        # determines if the color to play should be displayed.
        MULTICOLOR_COLLECTIONS = ["gokyo-shumyo", "xuanxuan-qijing", "igo-hatsuyoron"]

        state_color_to_play = (
            force_color_to_play
            or random_color
            or (
                color_to_play == "default"
                and any(term in collection for term in MULTICOLOR_COLLECTIONS)
            )
        )

        # the text to be displayed is determined.
        if "gokyo-shumyo" in collection:
            reverse_dict = {value: key for key, value in GOKYO_SHUMYO_SECTIONS.items()}
            section_num = reverse_dict[section_name]
            text_str = f"problem {section_num}-{problem_num}"
        else:
            text_str = f"problem {problem_num}"

        if state_color_to_play:
            if color_to_play == "default":
                color_str = default_to_play
            else:
                color_str = color_to_play
            text_str += f", {color_to_play} to play"

        text_image = create_text_image(text_str, text_rgb, text_height_in)

        TEXT_PADDING_TOP = TEXT_PADDING_TOP_IN * DPI
        TEXT_PADDING_BOTTOM = TEXT_PADDING_BOTTOM_IN * DPI

        additional_height = int(
            text_image.size[1] + TEXT_PADDING_TOP + TEXT_PADDING_BOTTOM
        )

        """
        Step 6) Combines the diagram and label as one image.
        """
        w, h = board.size
        new_image = Image.new("RGB", (w, h + additional_height), (255, 255, 255))
        new_image.paste(board, (0, 0))

        text_x = int(w / 2 - text_image.size[0] / 2)
        new_image.paste(text_image, (text_x, int(h + TEXT_PADDING_TOP)))

        board = new_image

    return board
