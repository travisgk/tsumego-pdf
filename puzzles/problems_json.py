import json
import os

def _flip_text_horizontally(problem_str: str):
    """ Returns the problem string with its stones flipped across the Y-axis. """
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


def read_problems_from_file(file_name: str):
    """ Returns a dict with a string for each Go puzzle. """
    GOKYO_SHUMYO_SECTIONS = {
        1: "living", 2: "killing", 3: "ko", 4: "capturing-race",
        5: "oiotoshi", 6: "connecting", 7: "various",
    }

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
            if any(clean_line.startswith(c) for c in "123456789"):
                # a full problem is shown before the page number,
                # so we can reset the searching variables.
                problem_identified = False
                current_problem_str = ""
                pass

            elif clean_line.startswith("problem"):
                # this line of the file provides information about the problem.
                if "cho" in file_name: 
                    # this problem is from a Cho collection.
                    problem_num = int(clean_line[len("problem "):])
                    problems[problem_num] = "B" + current_problem_str.strip()

                elif "gokyo-shumyo" in file_name: 
                    # this problem is from the Gokyo Shumyo.
                    hyphen_index = clean_line.find("-")
                    comma_index = clean_line.find(",")
                    
                    section_num = int(clean_line[len("problem "):hyphen_index])
                    problem_num = int(clean_line[hyphen_index+1:comma_index])
                    black_to_play = "black" in clean_line

                    section_name = GOKYO_SHUMYO_SECTIONS[section_num]
                    if problems.get(section_name) is None:
                        problems[section_name] = {}

                    color_label = "B" if black_to_play else "W"
                    problems[section_name][problem_num] = color_label + current_problem_str.strip()
                
                else:
                    # this problem is from a different collection.
                    comma_index = clean_line.find(",")
                    problem_num = int(clean_line[len("problem "):comma_index])
                    black_to_play = "black" in clean_line

                    color_label = "B" if black_to_play else "W"
                    problem_str = current_problem_str.strip()
                    if "igo-hatsuyoron" in file_name:
                        # the problems in the Hatsuyoron are oriented in the top-right,
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
        "igo-hatsuyoron": read_problems_from_file("igo-hatsuyoron.txt"), # on right
    }

    with open(out_path, "w") as json_file:
        json.dump(problems, json_file, indent=4)  # 'indent' makes the file more readable
