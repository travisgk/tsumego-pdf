"""
This example generates a diagram and saves it 
from directly given LaTeX string.
"""

import tsumego_pdf


def main():
    
    """
    This is a 19x19 template.
    
    latex_str = (
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
        ",!)))))))))))))!!!. "
    )
    """

    latex_str = (
        "W<(((((((((((((((((> "
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

    diagram.save("diagram.png")


if __name__ == "__main__":
    main()
