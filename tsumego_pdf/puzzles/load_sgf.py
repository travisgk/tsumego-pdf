def _find_index_of_first_upper(contents: str, start: int = 0):
    for i in range(start, len(contents)):
        if contents[i].isupper():
            return i

    return -1


def load_problem_from_sgf(file_path: str):
    """
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
    with open(file_path, "r", encoding="utf-8") as file:
        contents = file.read().strip()

    start_index = contents.find("SZ[")
    end_index = contents.find("]", start_index)
    size_str = contents[start_index + len("SZ[") : end_index]
    colon_index = size_str.find(":")
    if colon_index >= 0:
        width = int(size_str[:colon_index])
        height = int(size_str[colon_index + 1 :])
    else:
        width, height = int(size_str), int(size_str)

    # creates board.
    board = [[0 for _ in range(height)] for _ in range(width)]

    pl_index = contents.find("PL[")
    if pl_index >= 0:
        end_index = contents.find("]", pl_index)
        to_play = contents[pl_index + len("PL[") : end_index]
        color_to_play = "black" if to_play == "B" else "white"
    else:
        color_to_play = "black"

    ab_index = contents.find("AB[")
    aw_index = contents.find("AW[")
    if ab_index < 0:
        start_index = aw_index
    elif aw_index < 0:
        start_index = ab_index
    else:
        start_index = min(ab_index, aw_index)

    contents = contents[start_index:]

    # places initial stones.
    add_black_str, add_white_str = "", ""
    if ab_index >= 0:
        end_index = _find_index_of_first_upper(contents, start=ab_index)
        add_black_str = contents[ab_index:end_index]

    if aw_index >= 0:
        end_index = _find_index_of_first_upper(contents, start=aw_index)
        add_white_str = contents[aw_index:end_index]

    # TODO: implement rest of SGF reading.

    # (;GM[1]FF[4]CA[UTF-8]AP[Sabaki:0.52.2]KM[6.5]SZ[19]DT[2024-12-26]AW[rr][qr][qq][mr][mq][op][oq][nq][ns]AB[qp][rq][sr][po][oo][np][mp][lp][lq][lr][ls][ms]AE[ro];B[or];W[nr];B[pr];W[ps];B[pq];W[os];B[pp];W[qs];B[rs])
