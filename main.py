import reportlab.lib.pagesizes
from reportlab.pdfgen import canvas
from diagram import DPI, make_diagram


MARGIN_LEFT_IN = 0.5
MARGIN_TOP_IN = 0.5
MARGIN_RIGHT_IN = 0.5
MARGIN_BOTTOM_IN = 0.5
COLUMN_WIDTH_IN = 0.25

def create_pages(
    page_size,
    category,
    landscape: bool=False,
    problems_nums=None,
    num_columns: int=2,
):
    w_in, h_in = page_size[0] / 72, page_size[1] / 72
    if landscape and w_in < h_in:
        placeholder = w_in
        w_in = h_in
        h_in = placeholder
        
    w, h = w_in * DPI, h_in * DPI

    # calculates margins.
    m_l, m_t = MARGIN_LEFT_IN * DPI, MARGIN_TOP_IN * DPI
    m_r, m_b = MARGIN_RIGHT_IN * DPI, MARGIN_BOTTOM_IN * DPI

    colspan = COLUMN_WIDTH_IN * DPI

    pages = []

    return pages


def main():
    page_size = reportlab.lib.pagesizes.letter

    board_graphic_width_in = 2 + 7/8

    #for cat in ["elementary", "intermediate", "advanced"]:
    #    for i in range(1, 1000):
    diagram = make_diagram(
        "elementary",
        189,
        board_graphic_width_in,
        random_flip=True,
    )
    diagram.show()
    """
    SYMBOLS = [
        "<",  # empty top-left
        "(",  # empty top
        "!",  # white
        ">",  # empty top-right
        "@",  # black
        "+",  # empty
        "*",  # empty with star point
        " ",  # move to next row
    ]
    """
    
        


if __name__ == "__main__":
    main()