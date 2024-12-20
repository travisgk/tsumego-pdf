"""
This example generates a PDF for US letter paper size
full of particular problems from 
Cho Chikun's Elementary Life & Death problems, where
black is always the color to play.

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

    collection_name = "cho-elementary"

    my_problems = [
        17, 30, 38, 43, 45,
        50, 54, 55, 60, 64,
        65, 66, 67, 75, 76,
        78, 80, 96, 97, 101,
    ]
    random.shuffle(my_problems)

    tsumego_pdf.create_pdf(
        collection_name,
        page_size,
        problems_out_path="tsumego.pdf",
        solutions_out_path="tsumego-key.pdf",
        problem_nums=my_problems,
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
