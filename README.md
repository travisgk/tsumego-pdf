# tsumego-pdf
This tool generates a PDF of selected problems from any of the following tsumego selections collections:
  - *Cho Chikun's Encyclopedia of Life &amp; Death: Elementary* (900 Problems, Solutions Available)
  - *Cho Chikun's Encyclopedia of Life &amp; Death: Intermediate* (861 Problems, Solutions Available)
  - *Cho Chikun's Encyclopedia of Life &amp; Death: Advanced* (792 Problems)
  - *Goyko Shumyo* (520 Problems)
  - *Xuanxuan Qijing* (347 Problems)
  - *Igo Hatsuyōron* (183 Problems)
<br>

![Tsumego](https://github.com/travisgk/tsumego-pdf/blob/main/example-outputs/outputs.png?raw=true)
The problems by default are flipped around random.<br>This program will also create a parallel PDF which will contain the answers to the selected problems (if solutions are available for the collection).

See output similar to the screenshot above in the [the example PDF](https://github.com/travisgk/tsumego-pdf/blob/main/example-outputs/demo-a.pdf) and its corresponding [answers PDF](https://github.com/travisgk/tsumego-pdf/blob/main/example-outputs/demo-a-key.pdf).

<br>

### "Why wouldn't I just solve these Go puzzles on my computer?"
- The lack of instant feedback helps you improve visualization skills and simulates actual gameplay.
- It discourages finding answers by trial-and-error.
- Paper and a slower pace builds deep focus and can be a more relaxing experience.
- It provides you a healthy break from digital devices.
- Solving puzzles on paper strengthens your ability to trust your own judgment and decisions in Go.
<br>

## Setup
You will need Pillow and ReportLab to run this program.
`pip install pillow reportlab`

<br>
<br>

## Usage
The following code selects creates a packet of 120 random problems from *Cho Chikun's Encyclopedia of Life &amp; Death: Elementary*, where some particular problems are explicitly set to appear somewhere.

This provides [a PDF with the tsumego](https://github.com/travisgk/tsumego-pdf/blob/main/example-outputs/tsumego%202024-12-23%20153538.pdf) and [a companion PDF with the solutions](https://github.com/travisgk/tsumego-pdf/blob/main/example-outputs/tsumego%202024-12-23%20153538%20key.pdf).

```
import random
import reportlab.lib.pagesizes
import tsumego_pdf

page_size = reportlab.lib.pagesizes.letter  # US letter paper size.

# defines the problems I previously had the most problems with.
collection_name = "cho-elementary"
problem_nums = [
    637, 416, 127, 476, 183, 521, 231, 293, 627,
    434, 288, 725, 523, 316, 422, 99, 657, 114,
]

# fills the list with other random problems until there are 120 total problems.
while len(problem_nums) < 120:
    rand_num = random.randint(1, 900)
    if rand_num not in problem_nums:
        problem_nums.append(rand_num)

# constructs the selections and shuffles.
problem_selections = [(num, collection_name) for num in problem_nums]
random.shuffle(problem_selections)

# writes the PDF.
tsumego_pdf.create_pdf(
    problem_selections,
    page_size,
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
    ratio_to_flip_xy=4/6,  # more likely to have puzzles shown vertically.
    verbose=True,  # shows progress bar.
)
```

<br>
<br>

## Print a Go Board
A Go board can be printed out to be used with actual Go stones. If you want to make a PDF, run:
```
tsumego_pdf.create_portable_board(
    paper_size=reportlab.lib.pagesizes.letter,
    landscape=True,
    board_size=(13, 9),
)
```
This will create a 13x9 Go board for a US letter paper size.

<br>
<br>

## Creating Blank Templates for Print

```
tsumego_pdf.create_blank_template(
    paper_size=reportlab.lib.pagesizes.letter,
    landscape=True,
    board_size=19,
    board_width_in=2.653,
    boards_per_col=3,  # width.
    boards_per_row=2,  # height.
    num_pages=1,
    draw_bbox_around_diagrams=True,
)
```
This will create a PDF of 3x2 boards of grid size 19x19.

<br>
<br>

## Notes
Problems **#218** and **#533** in the Elementary section of Cho Chikun's problems have been pointed out as unsolvable, so they've been tweaked for this repository. Problems **#344** and **#396** in the Intermediate section have been tweaked as well.

<br>

When bookbinding, keep in mind that the punch holes printed in a signature might vary location; make sure they line up manually.

<br>

The solutions come from online Go websites. They are presumed to be correct, but please raise an issue if you believe the solution presented is incorrect and specify the correct solution(s).

<br>

The options for `color_to_play` are:
- "default": The color to play will be as it appears in its original book.
- "black": The color to play will always be black; the color to play will not be specified in the label.
- "white": The color to play will always be white; the color to play will not be specified in the label.
- "random": The color to play will be random for each problem, and the label will say who's to move first.

<br>

The tsumego are prioritized to show up horizontally. If a puzzle is too thin, it won't be shown vertically because too many occurrences of this could make the PDF inefficient in using space. If you want to see thinner puzzles potentially flipped to be displayed vertically, then you need to lower the `ratio_to_flip_xy`. By default this is `5/6`, meaning the side lengths of the bounding box of a tsumego (all its stones and to the nearest corner) must have a ratio such that: `5/6` <= ratio <= `6/5`. The lower this fraction is, the more thinner puzzles you'll see potentially having their X/Y axes flipped.

<br>

Setting `problem_nums` to `None` will select all problems in the desired collection. This, however, will not randomize their order.

<br>
<br>

## Special Thanks
These entries were provided by Vít Brunner's collection of problems on his website [tasuki.org](https://tsumego.tasuki.org/).
