"""
This example generates a PDF for A4 size paper 
with random problems from the Gokyo Shumyo,
where white is always the color to play.
"""

import random
import reportlab.lib.pagesizes
import tsumego_pdf


def main():
    page_size = reportlab.lib.pagesizes.A4  # European paper size.

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

    collection_name = "gokyo-shumyo"

    # this collection has subsections, so those must be specified.
    my_problems = []
    my_problems.extend([(i, "living") for i in range(1, 104)])
    my_problems.extend([(i, "killing") for i in range(1, 72)])
    my_problems.extend([(i, "ko") for i in range(1, 91)])
    my_problems.extend([(i, "capturing-race") for i in range(1, 97)])
    my_problems.extend([(i, "oiotoshi") for i in range(1, 41)])
    my_problems.extend([(i, "connecting") for i in range(1, 75)])
    my_problems.extend([(i, "various") for i in range(1, 47)])

    # randomizes the problems.
    random.shuffle(my_problems)

    tsumego_pdf.create_pdf(
        collection_name,
        page_size,
        problems_out_path="gokyo.pdf",
        problem_nums=my_problems,
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
        verbose=True,  # shows progress bar
    )


if __name__ == "__main__":
    main()
