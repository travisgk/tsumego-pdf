from tsumego_pdf.puzzles.problems_json import get_problem


def get_num_stones_for_selections(selections: list):
    """
    Returns the number of black and white stones
    needed to recreate the puzzles specified by <selections>.
    """

    def count_stones(tsumego: str, is_black: bool):
        """Returns the number of stones in the tsumego."""
        num_stones = 0
        for c in tsumego:
            if (is_black and c == "@") or (not is_black and c == "!"):
                num_stones += 1

        return num_stones

    max_num_black_stones = 0
    max_num_white_stones = 0

    for selection in selections:
        problem_num = selection[0]
        collection_name = selection[1]
        section_name = None if len(selection) <= 2 else selection[2]

        problem_dict = get_problems(collection_name, section_name, problem_num)
        if problem_dict is None:
            return 0, 0
        tsumego_str = " ".join(problem_dict["lines"])

        num_black_stones = count_stones(tsumego_str, is_black=True)
        num_white_stones = count_stones(tsumego_str, is_black=False)

        max_num_black_stones = max(max_num_black_stones, num_black_stones)
        max_num_white_stones = max(max_num_white_stones, num_white_stones)

    return max_num_black_stones, max_num_white_stones
