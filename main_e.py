"""
This example generates a PDF for US letter paper size
with a 50 problems from Cho's Intermediate collection,
where the color to play is random
and the problem numbers aren't displayed on the worksheet,
but are on the key.

The solution mark is also a star instead of an X.

A separate parallel PDF will also be created
which contains possible solutions.
"""

import random
import reportlab.lib.pagesizes
import tsumego_pdf


def main():
    """
    The available collections are:
        - "cho-elementary" (900 problems)
        - "cho-intermediate" (861 problems)
        - "cho-advanced" (792 problems)
        - "gokyo-shumyo" (520 problems)
            - "living" (103 problems)
            - "killing" (71 problems)
            - "ko" (90 problems)
            - "capturing-race" (96 problems)
            - "oiotoshi" (40 problems)
            - "connecting" (74 problems)
            - "various" (46 problems)
        - "xuanxuan-qijing" (347 problems)
        - "igo-hatsuyoron" (183 problems)
    """

    page_size = reportlab.lib.pagesizes.letter  # American paper size.
    margin_in = {"left": 0.6, "top": 0.6, "right": 0.6, "bottom": 1.0}

    collection_name = "cho-intermediate"
    problem_nums = random.sample(range(1, 862), 50)
    problem_selections = [(num, collection_name) for num in problem_nums]

    random.shuffle(problem_selections)

    tsumego_pdf.create_pdf(
        problem_selections,
        page_size,
        margin_in=margin_in,
        problems_out_path="50-intermediate.pdf",
        solutions_out_path="50-intermediate-key.pdf",
        color_to_play="random",
        landscape=False,
        num_columns=2,
        column_spacing_in=2.5,
        spacing_below_in=1,
        placement_method="block",
        show_problem_num=False,
        draw_sole_solving_stone=True,
        solution_mark="star",
        problem_text_rgb=(128, 128, 128),
        solution_text_rgb=(128, 128, 128),
        include_page_num=False,
        display_width=13,
        verbose=True,  # shows progress bar
    )


if __name__ == "__main__":
    main()
