import json
import os
from .playout import give_resulting_board

_PROBLEMS = None


def _flip_text_horizontally(problem_str: str):
    """
    Returns the problem string with its stones flipped across the Y-axis.
    """
    lines = problem_str.split(" ")
    result = ""
    for i, raw_line in enumerate(lines):
        # left/right characters are swapped.
        line = raw_line.replace("<", "P")
        line = line.replace(">", "<")
        line = line.replace("P", ">")

        line = line.replace("[", "P")
        line = line.replace("]", "[")
        line = line.replace("P", "]")

        result += line[::-1]
        if i < len(lines) - 1:
            result += " "

    return result


GOKYO_SHUMYO_SECTIONS = {
    1: "living",
    2: "killing",
    3: "ko",
    4: "capturing-race",
    5: "oiotoshi",
    6: "connecting",
    7: "various",
}


def read_problems_from_file(file_name: str):
    """Returns a dict with a string for each Go puzzle."""

    problem_num = None
    current_problem_str = ""
    problem_identified = False

    # determines the file path to read from.
    local_dir = os.path.dirname(os.path.abspath(__file__))
    books_dir = "books"
    file_path = os.path.join(local_dir, books_dir, file_name)

    problems = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            clean_line = line.strip()
            if len(clean_line) <= 3 and any(clean_line.startswith(c) for c in "123456789"):
                # a full problem is shown before the page number,
                # so we can reset the searching variables.
                problem_identified = False
                current_problem_str = ""
                pass

            elif clean_line.startswith("problem"):
                # this line of the file provides information about the problem.
                if "cho" in file_name:
                    # this problem is from a Cho collection.
                    problem_num = int(clean_line[len("problem ") :])
                    problems[problem_num] = "B" + current_problem_str.strip()

                elif "gokyo-shumyo" in file_name:
                    # this problem is from the Gokyo Shumyo.
                    hyphen_index = clean_line.find("-")
                    comma_index = clean_line.find(",")

                    section_num = int(clean_line[len("problem ") : hyphen_index])
                    problem_num = int(clean_line[hyphen_index + 1 : comma_index])
                    black_to_play = "black" in clean_line

                    section_name = GOKYO_SHUMYO_SECTIONS[section_num]
                    if problems.get(section_name) is None:
                        problems[section_name] = {}

                    color_label = "B" if black_to_play else "W"
                    problems[section_name][problem_num] = (
                        color_label + current_problem_str.strip()
                    )

                else:
                    # this problem is from a different collection.
                    comma_index = clean_line.find(",")
                    problem_num = int(clean_line[len("problem ") : comma_index])
                    black_to_play = "black" in clean_line

                    color_label = "B" if black_to_play else "W"
                    problem_str = current_problem_str.strip()
                    if "igo-hatsuyoron" in file_name:
                        # the problems in the Hatsuyoron
                        # are oriented in the top-right,
                        # so they're flipped to match the rest of the data.
                        problem_str = _flip_text_horizontally(problem_str)

                    problems[problem_num] = color_label + problem_str

                current_problem_str = ""  # resets.

            else:
                # this line is part of a problem,
                # so it's simply added to the string.
                if len(current_problem_str) == 0:
                    current_problem_str = clean_line
                else:
                    current_problem_str += " " + clean_line
    return problems


def create_problems_json(out_path: str):
    problems = {
        "cho-elementary": read_problems_from_file("cho-elementary.txt"),
        "cho-intermediate": read_problems_from_file("cho-intermediate.txt"),
        "cho-advanced": read_problems_from_file("cho-advanced.txt"),
        "gokyo-shumyo": read_problems_from_file("gokyo-shumyo.txt"),
        "xuanxuan-qijing": read_problems_from_file("xuanxuan-qijing.txt"),
        "igo-hatsuyoron": read_problems_from_file("igo-hatsuyoron.txt"),  # on right
    }

    with open(out_path, "w") as json_file:
        json.dump(
            problems, json_file, indent=4
        )  # 'indent' makes the file more readable


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


def get_problem(
    collection_name=None,
    section_name=None,
    problem_num=None,
    latex_str=None,
    play_out_solution: bool = False,
):
    """Returns a dictionary with information about a problem."""
    _load_problems()

    if collection_name is None and latex_str is None:
        print(
            "No problem was specified. make_diagram needs to be given a "
            "problem selection or a LaTeX string."
        )
        return None

    if collection_name is not None:
        collection_name = collection_name.lower()
        problem_collection = _PROBLEMS.get(collection_name)
        if problem_collection is None:
            print(
                f"'{collection}'' is not an available collection. "
                "Only the following are accepted:"
            )
            for key in _PROBLEMS.keys():
                print(f'\t- "{key}"')

            return None

        if section_name is not None:
            # the section name must be considered.
            section = problem_collection.get(section_name)
            if section is None:
                print(
                    f"The collection '{collection_name}' does not have "
                    f"a section named {section_name}."
                )
                return None

            lines = section.get(str(problem_num))
            if lines is None:
                print(
                    f"The section '{section_name}' of {collection_name} "
                    f"does not have a problem numbered #{problem_num}."
                )
                return None

        else:
            lines = problem_collection.get(str(problem_num))
            if lines is None:
                print(
                    f"The collection '{collection_name}' does not have "
                    f"a problem numbered #{problem_num}."
                )
                return None
    else:
        lines = latex_str

    lines = lines.split(" ")
    default_to_play = "black" if lines[0][0] == "B" else "white"
    lines[0] = lines[0][1:]  # snips off the color-to-play info.

    num_solutions = 0
    max_x = 0
    max_y = 0
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            if c in "@!":  # a stone.
                max_x = max(max_x, x)
                max_y = max(max_y, y)
            if c == "X":
                num_solutions += 1

    if play_out_solution and num_solutions == 1:
        lines = give_resulting_board(lines, default_to_play) # TODO: set equal to

    return {
        "show-width": max_x + 1,  # how many stones wide.
        "show-height": max_y + 1,  # how many stones high.
        "lines": lines,
        "default-to-play": default_to_play,
    }
