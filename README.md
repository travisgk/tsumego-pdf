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
The following code selects 100 random problems from *Cho Chikun's Encyclopedia of Life &amp; Death: Elementary* and 100 random problems from *Cho Chikun's Encyclopedia of Life &amp; Death: Intermediate*, mixes them all together, and then saves a PDF with invisible labels and another PDF with the problems labelled and solutions provided.

This provides [a PDF with the tsumego](https://github.com/travisgk/tsumego-pdf/blob/main/example-outputs/demo-c.pdf) and [a companion PDF with the solutions](https://github.com/travisgk/tsumego-pdf/blob/main/example-outputs/demo-c-key.pdf).

```
import random
import reportlab.lib.pagesizes
import tsumego_pdf

problem_selections = []

# adds 100 random problems from Cho's Elementary Life & Death.
collection_name = "cho-elementary"
problem_nums = random.sample(range(1, 901), 100)
problem_selections.extend([(num, "cho-elementary") for num in problem_nums])

# adds 100 random problems from Cho's Intermediate Life & Death.
collection_name = "cho-intermediate"
problem_nums = random.sample(range(1, 862), 100)
problem_selections.extend([(num, "cho-intermediate") for num in problem_nums])

# shuffles all the selections.
random.shuffle(problem_selections)


page_size = reportlab.lib.pagesizes.letter  # US letter paper size.
margin_in = {  # print margins in inches.
  "left": 0.5, "top": 0.5, "right": 0.5, "bottom": 0.5
}

tsumego_pdf.create_pdf(
    problem_selections,
    page_size,
    margin_in=margin_in,
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
```

Setting `problem_nums` to `None` will select all problems in the desired collection.

<br>
<br>

## Notes
Problems **#218** and **#533** in the Elementary section of Cho Chikun's problems have been pointed out as unsolvable, so they've been tweaked for this repository. Problems **#344** and **#396** in the Intermediate section have been tweaked as well.

<br>

The solutions come from online Go websites. They are presumed to be correct, but please raise an issue if you believe the solution presented is incorrect and specify the correct solution(s).

<br>

The options for `color_to_play` are:
- "default": The color to play will be as it appears in its original book.
- "black": The color to play will always be black; the color to play will not be specified in the label.
- "white": The color to play will always be white; the color to play will not be specified in the label.
- "random": The color to play will be random for each problem, and the label will say who's to move first.

<br>
<br>

## Special Thanks
These entries were provided by Vít Brunner's collection of problems on his website [tasuki.org](https://tsumego.tasuki.org/).
