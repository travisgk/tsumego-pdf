"""
This example generates a PDF for US letter paper size
full of a mix of 100 random problems from 
Cho Chikun's Elementary Life & Death problems and 100 other
random problems from Cho Chikun's Intermediate Life & Death problems.
Black is always the color to play.

A separate parallel PDF will also be created
which contains possible solutions.
"""

import random
import reportlab.lib.pagesizes
import tsumego_pdf


def main():
    page_size = reportlab.lib.pagesizes.letter  # American paper size.

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

    problem_selections = []

    # adds 100 random problems from Cho's Elementary Life & Death.
    collection_name = "cho-elementary"
    problem_nums = random.sample(range(1, 901), 100)
    problem_selections.extend([(num, "cho-elementary") for num in problem_nums])

    # adds 100 random problems from Cho's Intermediate Life & Death.
    collection_name = "cho-intermediate"
    problem_nums = random.sample(range(1, 861), 100)
    problem_selections.extend([(num, "cho-intermediate") for num in problem_nums])

    # shuffles all the selections.
    random.shuffle(problem_selections)

    tsumego_pdf.create_pdf(
        problem_selections,
        page_size,
        problems_out_path="random-200-mix.pdf",
        solutions_out_path="random-200-mix-key.pdf",
        color_to_play="black",
        landscape=False,
        num_columns=2,
        column_spacing_in=3,
        spacing_below_in=1,
        placement_method="block",
        include_text=True,
        problem_text_rgb=(255, 255, 255),
        solution_text_rgb=(128, 128, 128),
        include_page_num=True,
        display_width=12,
        verbose=True,  # shows progress bar
    )


if __name__ == "__main__":
    main()
