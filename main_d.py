"""
This example generates a PDF for US letter paper size
with a few problems from Cho's Beginner collection.
The diagrams are made to be posted on a wall.

A separate parallel PDF will also be created
which contains possible solutions.
"""

import random
import reportlab.lib.pagesizes
import tsumego_pdf


def main():
    page_size = reportlab.lib.pagesizes.letter  # American paper size.
    margin_in = {"left": 0.6, "top": 0.6, "right": 0.6, "bottom": 1.0}

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
    problem_nums = [
        22, 80, 205, 115, 190, 223, 21, 160, 266, 235, 275, 79, 218, 231, 187
    ]
    problem_selections = [(num, collection_name) for num in problem_nums]
    random.shuffle(problem_selections)

    tsumego_pdf.create_pdf(
        problem_selections,
        page_size,
        margin_in=margin_in,
        problems_out_path="wall-display.pdf",
        solutions_out_path="wall-display-key.pdf",
        color_to_play="black",
        landscape=False,
        num_columns=1,
        column_spacing_in=2.5,
        spacing_below_in=1,
        placement_method="block",
        include_text=False,
        create_key = True,
        draw_sole_solving_stone = True,
        solution_mark = "star",
        problem_text_rgb=(255, 255, 255),
        solution_text_rgb=(128, 128, 128),
        include_page_num=False,
        display_width=12,
        outline_thickness_in=1/32,
        line_width_in=1/36,
        star_point_radius_in=1/16,
        draw_bbox_around_diagrams=True,
        verbose=True,  # shows progress bar
    )


if __name__ == "__main__":
    main()
