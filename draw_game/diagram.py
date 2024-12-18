import json
import os
import random
from PIL import Image, ImageDraw
from puzzles.problems_json import create_problems_json
from .board_graphics import *



# this is the display width for the board. 11 is the min.
_display_width = 12 # 12


_PROBLEMS = None
def get_problems():
    """Returns a dictionary containing all the Go problems."""
    _load_problems()
    return _PROBLEMS


def _load_problems():
    """ Loads all the problems to memory if not done yet."""
    global _PROBLEMS
    if _PROBLEMS is not None:
        return

    local_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(local_dir, "puzzles", "go-problems.json")

    if not os.path.exists(file_path):
        create_problems_json(file_path)
  
    with open(file_path, "r") as file:
        _PROBLEMS = json.load(file)
    


def calc_stone_size(diagram_width_in):
    cells_wide = min(19, _display_width)
    stone_size_in = diagram_width_in / cells_wide
    stone_size_px = stone_size_in * DPI

    return int(stone_size_px)


def make_diagram(
    collection: str,
    problem_num: int,
    diagram_width_in,
    color_to_play: str="default",
    flip_xy: bool=True,
    flip_x: bool=True,
    flip_y: bool=True,
    include_text: bool=True,
    placement_method: str="block",
    force_color_to_play: bool=False,
    create_key: bool=False,
    text_rgb: tuple=(128, 128, 128),
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
        problem_num (int): the problem number.
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
        placement_method (str): the method used to place diagrams:
            - "none": places diagrams without regarding any alignment.
            - "block": diagrams are placed to have 
                       stone lines match up across columns.
        force_color_to_play (bool): if True, the label "black/white to play"
                                    is shown no matter what.
        create_key (bool): if True, the problem solution(s) is/are marked.
    """
    
    # determine the stone size.
    stone_size_px = calc_stone_size(diagram_width_in)
    
    # determines color to play.
    random_color = False
    if color_to_play == "random":
        random_color = True
        color_to_play = random.choice(["black", "white"])

    # draws a full board.
    full_board_width_in = (stone_size_px * 19) / DPI
    board, board_draw = draw_board(width_in=full_board_width_in)

    # loads the Cho Chikun problems if not yet done,
    # then selects the problem.
    _load_problems()

    collection = collection.lower()
    lines = _PROBLEMS.get(collection)
    if lines is None:
        print(f"'{collection}'' is not an available collection. Only the following are accepted:")
        for key in _PROBLEMS.keys():
            print(f"\t- \"{key}\"")
        #print("\t- Elementary\n\t- Intermediate\n\t- Advanced")
        return None

    lines = lines.get(str(problem_num))
    if lines is None:
        print(f"The collection '{collection}' does not have a problem numbered #{problem_num}.")
        return None

    lines = lines.split(" ")
    default_to_play = "black" if lines[0][0] == "B" else "white"
    lines[0] = lines[0][1:]

    # draws the stones for the puzzle 
    # while finding the bbox for the stones themselves.
    max_x, max_y = 0, 0

    
    invert_colors = color_to_play != "default" and default_to_play != color_to_play

    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            if c == "@": # black stone.
                draw_stone(board, x, y, stone_size_px, is_black=not invert_colors)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
            elif c == "!": # white stone.
                draw_stone(board, x, y, stone_size_px, is_black=invert_colors)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
            elif create_key and c == "X": # solution.
                draw_mark(board, x, y, stone_size_px, is_black=not invert_colors)

    # flipping the X and Y axes is forbidden/enforced depending on
    # the bbox attributes.
    if 0.9 < abs(max_x / max_y) < 1.1:
        # the bbox is relatively square, so it won't be visually jarring
        # to let it be flipped diagonally either way.
        pass
    elif max_x > _display_width - 2:
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

    if flip_x:
        is_top = not is_top

    if flip_y:
        is_left = not is_left

    # crops the puzzle.
    w, h = board.size
    left = 0 if is_left else w - stone_size_px * _display_width
    right = left + stone_size_px * _display_width
    top = 0 if is_top else h - stone_size_px * (max_y + 2)
    bottom = top + stone_size_px * (max_y + 2)
    
    board = board.crop((left, top, right, bottom))


    if include_text:
        # draws text if a problem label will be included.
        state_color_to_play = (
            force_color_to_play or random_color
            or (
                color_to_play == "default" 
                and any(
                    term in collection 
                    for term in ["gokyo-shumyo", "xuanxuan-qijing", "igo-hatsuyoron"]
                )
            )
        )

        text_str = f"problem {problem_num}"
        if state_color_to_play:
            text_str += ", " + (color_to_play if color_to_play != "default" else default_to_play) + " to play"
        text_image = create_text_image(text_str, text_rgb)


        # adds the text image if specified.
        TEXT_PADDING_TOP = TEXT_PADDING_TOP_IN * DPI
        TEXT_PADDING_BOTTOM = TEXT_PADDING_BOTTOM_IN * DPI

        # determines spacing below.
        additional_height = text_image.size[1] + TEXT_PADDING_TOP + TEXT_PADDING_BOTTOM
        if placement_method == "block":
            additional_height = int(stone_size_px * (int(additional_height / stone_size_px) + 1))

        w, h = board.size
        additional_height = int(text_image.size[1] + TEXT_PADDING_TOP + TEXT_PADDING_BOTTOM)
        new_image = Image.new("RGB", (w, h + additional_height), (255, 255, 255))
        new_image.paste(board, (0, 0))

        text_x = int(w/2 - text_image.size[0]/2)
        new_image.paste(text_image, (text_x, int(h + TEXT_PADDING_TOP)))

        board = new_image


    return board