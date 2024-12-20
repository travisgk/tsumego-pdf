# tsumego-pdf
This tool generates a PDF of selected problems from any of the following tsumego selections collections:
  - *Cho Chikun's Encyclopedia of Life &amp; Death: Elementary* (Solutions Available)
  - *Cho Chikun's Encyclopedia of Life &amp; Death: Intermediate*
  - *Cho Chikun's Encyclopedia of Life &amp; Death: Advanced*
  - *Goyko Shumyo*
  - *Xuanxuan Qijing*
  - *Igo Hatsuyo-ron*
<br>

![Tsumego](https://github.com/travisgk/tsumego-pdf/blob/main/example-outputs/outputs.png?raw=true)
The problems can be set to be flipped around randomly, as well as setting the color to play.<br>This program will also by default create a parallel PDF which will contain the answers to the selected problems (if solutions are available for the collection).

See the above output in full in the [the example PDF](https://github.com/travisgk/tsumego-pdf/blob/main/example-outputs/tsumego.pdf) and its corresponding [answers PDF](https://github.com/travisgk/tsumego-pdf/blob/main/example-outputs/tsumego-key.pdf)

<br>

## Usage
This selects various problems from *Cho Chikun's Encyclopedia of Life &amp; Death: Elementary* and saves one PDF with invisible labels and another PDF with the problems labelled and solutions provided.

```
import random
import reportlab.lib.pagesizes
from puzzle_pdf import create_pdf

page_size = reportlab.lib.pagesizes.letter  # American paper size.
collection_name = "cho-elementary"

my_problems = [
    17, 30, 38, 43, 45,
    50, 54, 55, 60, 64,
    65, 66, 67, 75, 76,
    78, 80, 96, 97, 101,
]
random.shuffle(my_problems)

create_pdf(
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
```

<br>

## Notes
Problems **#218** and **#533** in the Elementary section of Cho Chikun's problems have been pointed out as unsolvable, so they've been tweaked for this repository.

<br>

## Special Thanks
These entries were provided by Vít Brunner's collection of problems on his website [tasuki.org](https://tsumego.tasuki.org/).
