""" 
This demo creates a printable booklet that's composed of five signatures
that can be bound together using bookbinding.

A solution key will also be saved.
"""

import time
import random
import reportlab.lib.pagesizes
import tsumego_pdf


def main():
    start_time = time.time()

    # settings.
    page_size = reportlab.lib.pagesizes.letter  # American paper size.
    margin_in = {
        "left": 0.5,
        "right": 0.5,
        "top": 0.5,
        "bottom": 0.5,
    }

    # selects and randomizes particular problems.
    collection_name = "cho-elementary"
    
    TOTAL = 361
    while len(problem_nums) < TOTAL:
        rand_num = random.randint(1, 900)

        if rand_num not in problem_nums and rand_num not in hard_problem_nums:
            problem_nums.append(rand_num)

    problem_selections = [(num, collection_name) for num in problem_nums]
    random.shuffle(problem_selections)

    tsumego_pdf.create_pdf(
        problem_selections,
        page_size,
        margin_in=margin_in,
        color_to_play="black",
        landscape=True,
        num_columns=1,
        column_spacing_in=1,
        spacing_below_in=1 / 2,
        placement_method="block-proportional",
        include_text=True,
        problem_text_rgb=(255, 255, 255),
        solution_text_rgb=(171, 171, 171),
        include_page_num=False,
        display_width=13,
        draw_sole_solving_stone=False,
        verbose=True,  # shows progress bar
        is_booklet=True,
        num_signatures=5,
        booklet_cover="japanese",
        embed_cover_in_signatures=True,
        booklet_center_padding_in=4.5,
        ratio_to_flip_xy=9 / 13,
        booklet_key_in_printers_spread=False,  # True
        solution_mark="x",
        line_width_in=1/72,
        outline_thickness_in=1/78,
    )

    elapsed = time.time() - start_time
    print(f"that took {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()
