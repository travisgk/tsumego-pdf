"""
This file contains six different demos to produce PDFs.
"""

import time
import random
import reportlab.lib.pagesizes
import tsumego_pdf

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


def demo_a():
    start_time = time.time()
    """
    This example generates a PDF that's a double-sided booklet 
    made for US letter paper size that's full of particular problems from 
    Cho Chikun's Elementary Life & Death problems, where
    black is always the color to play.

    A separate parallel PDF will also be created
    which contains possible solutions.
    """

    page_size = reportlab.lib.pagesizes.letter  # American paper size.

    margin_in = {
        "left": 0.5,
        "right": 0.5,
        "top": 0.5,
        "bottom": 0.5,
    }

    # specifies particular problems.
    collection_name = "cho-elementary"
    problem_nums = [
        657,
        617,
        490,
        724,
        719,
        741,
        564,
        345,
        34,
        340,
        470,
        238,
        370,
        390,
        747,
        126,
        810,
        870,
    ]

    # fills the list with other random problems until there are 35 total problems.
    while len(problem_nums) < 35:
        rand_num = random.randint(1, 900)
        if rand_num not in problem_nums:
            problem_nums.append(rand_num)

    problem_selections = [(num, collection_name) for num in problem_nums]
    random.shuffle(problem_selections)

    tsumego_pdf.create_pdf(
        problem_selections,
        page_size,
        margin_in=margin_in,
        problems_out_path="demo-a.pdf",
        solutions_out_path="demo-a-key.pdf",
        color_to_play="black",
        landscape=True,
        num_columns=1,
        column_spacing_in=1,
        spacing_below_in=1 / 2,
        placement_method="block-proportional",
        include_text=True,
        problem_text_rgb=(255, 255, 255),
        solution_text_rgb=(128, 128, 128),
        include_page_num=False,
        display_width=13,
        verbose=True,  # shows progress bar
        is_booklet=True,
        booklet_cover="japanese",
        booklet_center_padding_in=4.25,
    )

    elapsed = time.time() - start_time
    print(f"that took {elapsed:.2f} seconds")


def demo_b():
    """
    This example generates a PDF for A4 size paper
    with 100 random problems from the Gokyo Shumyo,
    where white is always the color to play.
    """

    page_size = reportlab.lib.pagesizes.A4  # European paper size.

    collection_name = "gokyo-shumyo"

    # this collection has subsections, so those must be specified.
    selections = []
    selections.extend([(i, collection_name, "living") for i in range(1, 104)])
    selections.extend([(i, collection_name, "killing") for i in range(1, 72)])
    selections.extend([(i, collection_name, "ko") for i in range(1, 91)])
    selections.extend([(i, collection_name, "capturing-race") for i in range(1, 97)])
    selections.extend([(i, collection_name, "oiotoshi") for i in range(1, 41)])
    selections.extend([(i, collection_name, "connecting") for i in range(1, 75)])
    selections.extend([(i, collection_name, "various") for i in range(1, 47)])

    # randomizes the problems.
    random.shuffle(selections)
    selections = selections[:100]

    tsumego_pdf.create_pdf(
        selections,
        page_size,
        problems_out_path="demo-b.pdf",
        color_to_play="white",
        landscape=False,
        num_columns=3,
        column_spacing_in=1,
        spacing_below_in=0.75,
        placement_method="block",
        include_text=True,
        create_key=False,
        include_page_num=True,
        text_height_in=0.1,
        display_width=19,
        star_point_radius_in=1 / 64,
        verbose=True,  # shows progress bar
    )


def demo_c():
    """
    This example generates a PDF for US letter paper size
    full of a mix of 100 random problems from
    Cho Chikun's Elementary Life & Death problems and 100 other
    random problems from Cho Chikun's Intermediate Life & Death problems.
    Black is always the color to play.

    A separate parallel PDF will also be created
    which contains possible solutions.
    """

    page_size = reportlab.lib.pagesizes.letter  # American paper size.
    margin_in = {"left": 0.6, "top": 0.6, "right": 0.6, "bottom": 0.6}

    problem_selections = []

    # adds 15 random problems from Cho's Elementary Life & Death.
    collection_name = "cho-elementary"
    problem_nums = random.sample(range(1, 901), 15)
    problem_selections.extend([(num, "cho-elementary") for num in problem_nums])

    # adds 15 random problems from Cho's Intermediate Life & Death.
    collection_name = "cho-intermediate"
    problem_nums = random.sample(range(1, 861), 15)
    problem_selections.extend([(num, "cho-intermediate") for num in problem_nums])

    # shuffles all the selections.
    random.shuffle(problem_selections)

    tsumego_pdf.create_pdf(
        problem_selections,
        page_size,
        margin_in=margin_in,
        problems_out_path="demo-c.pdf",
        solutions_out_path="demo-c-key.pdf",
        color_to_play="black",
        landscape=False,
        num_columns=2,
        column_spacing_in=2.5,
        spacing_below_in=1,
        placement_method="block",
        include_text=True,
        create_key=True,
        draw_sole_solving_stone=True,
        solution_mark="star",
        problem_text_rgb=(255, 255, 255),
        solution_text_rgb=(128, 128, 128),
        include_page_num=True,
        display_width=13,
        verbose=True,  # shows progress bar
    )


def demo_d():
    """
    This example generates a PDF for US letter paper size
    with a few problems from Cho's Beginner collection.
    The diagrams are made to be posted on a wall.

    A separate parallel PDF will also be created
    which contains possible solutions.
    """
    page_size = reportlab.lib.pagesizes.letter  # American paper size.
    margin_in = {"left": 0.6, "top": 0.6, "right": 0.6, "bottom": 0.6}

    collection_name = "cho-elementary"
    problem_nums = [
        637,
        416,
        127,
        476,
        183,
        521,
        231,
        293,
        627,
        434,
        288,
        725,
        523,
        316,
        422,
        99,
        657,
        114,
    ]

    problem_selections = [(num, collection_name) for num in problem_nums]
    random.shuffle(problem_selections)

    tsumego_pdf.create_pdf(
        problem_selections,
        page_size,
        margin_in=margin_in,
        problems_out_path="demo-d.pdf",
        solutions_out_path="demo-d-key.pdf",
        color_to_play="black",
        landscape=False,
        num_columns=1,
        column_spacing_in=2.5,
        spacing_below_in=0,
        placement_method="block",
        include_text=False,
        create_key=True,
        random_flip=True,
        draw_sole_solving_stone=False,
        solution_mark="big-star",
        problem_text_rgb=(255, 255, 255),
        solution_text_rgb=(128, 128, 128),
        include_page_num=False,
        display_width=12,
        outline_thickness_in=1 / 24,
        line_width_in=1 / 36,
        star_point_radius_in=1 / 16,
        draw_bbox_around_diagrams=True,
        verbose=True,  # shows progress bar
    )


def demo_e():
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
        problems_out_path="demo-e.pdf",
        solutions_out_path="demo-e-key.pdf",
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


def demo_f():
    """
    This example generates a diagram and saves it
    from directly given LaTeX string.
    """

    """
    This is a 19x19 template with black to play.
    
    latex_str = (
        "B"
        "<(((((((((((((((((> "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        "[++*+++++*+++++*++] "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        "[++*+++++*+++++*++] "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        "[++*+++++*+++++*++] "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        ",))))))))))))))))). "
    )
    """
    # white to play. this example shows invading too early.
    latex_str = (
        "W"
        "<(((((((((((((((((> "
        "[+++++++++++++++++] "
        "[++++!++++++++++++] "
        "[++!+++++*+++++*@+] "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        "[++*+++++*+++++*++] "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        "[+++++++++++++++++] "
        "[+++++++++++++++@+] "
        "[+++++++++++++++++] "
        "[++!+++++*+++++*++] "
        "[++++++++@++X++@++] "
        "[+++++++++++++++++] "
        ",))))))))))))))))). "
    )

    diagram_width_in = 2

    diagram = tsumego_pdf.make_diagram(
        diagram_width_in,
        latex_str=latex_str,
        color_to_play="default",
        flip_xy=False,
        flip_x=False,
        flip_y=False,
        include_text=False,
        show_problem_num=False,
        create_key=True,
        draw_sole_solving_stone=False,
        solution_mark="x",
        display_width=19,
        outline_thickness_in=1 / 128,
        line_width_in=1 / 128,
        star_point_radius_in=1 / 64,
    )

    diagram.save("demo-f.png")


if __name__ == "__main__":
    demo_a()
    demo_b()
    demo_c()
    demo_d()
    demo_e()
    demo_f()
