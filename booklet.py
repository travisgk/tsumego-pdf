import time
import random
import reportlab.lib.pagesizes
import tsumego_pdf


def main():
    start_time = time.time()

    # settings.
    page_size = reportlab.lib.pagesizes.letter  # American paper size.

    # selects and randomizes particular problems.
    collection_name = "cho-elementary"
    
    """
    hard_problem_nums = [
        21,
        33,
        121,
        122,
        125,
        204,
        212,
        231,
        241,
        251,
        273,
        333,
        466,
        470,
        498,
        514,
        518,
        575,
        578,
        635,
        711,
        736,
        789,
        820,
        831,
        833,
        835,
        837,
        865,
        444,
        540,
        653,
        697,
        50,
        51,
        130,
        167,
        193,
        239,
        391,
        520,
        573,
        647,
        686,
        689,
        770,
        807,
        815,
        220,
        317,
        429,
        579,
        598,
        723,
        766,
        773,
        818,
        64,
        161,
        177,
        199,
        223,
        245,
        248,
        257,
        298,
        322,
        332,
        342,
        390,
        427,
        446,
        455,
        471,
        479,
        486,
        506,
        513,
        531,
        561,
        576,
        615,
        619,
        624,
        633,
        641,
        664,
        748,
        870,
        255,
        258,
        272,
        304,
        394,
        412,
        473,
        474,
        595,
        139,
        415,
        126,
        266,
        493,
        523,
        551,
        55,
        99,
        164,
        305,
        312,
        324,
        326,
        341,
        345,
        380,
        408,
        477,
        521,
        695,
        715,
        874,
        559,
        567,
        203,
        353,
        417,
        460,
        494,
        553,
        607,
        621,
        657,
        714,
        808,
        861,
        893,
    ]

    step = len(hard_problem_nums) // 3

    problem_nums_a = hard_problem_nums[:step]
    problem_nums_b = hard_problem_nums[step : step * 2]
    problem_nums_c = hard_problem_nums[step * 2 :]
    problem_lists = [problem_nums_a, problem_nums_b, problem_nums_c]

    not_marked = [i for i in range(1, 901) if i not in hard_problem_nums]
    random.shuffle(not_marked)

    step = len(not_marked) // 3
    problem_nums_a.extend(not_marked[:step])
    problem_nums_b.extend(not_marked[step : step * 2])
    problem_nums_c.extend(not_marked[step * 2 :])

    TOTAL = 361
    with open("problem-nums.txt", "w") as file:
        for i, problem_nums in enumerate(problem_lists):
            while len(problem_nums) < TOTAL:
                rand_num = random.randint(1, 900)

                if rand_num not in problem_nums and rand_num not in hard_problem_nums:
                    problem_nums.append(rand_num)

            problem_selections = [(num, collection_name) for num in problem_nums]
            random.shuffle(problem_selections)

            margin_in = {
                "left": 0.5,
                "right": 0.5,
                "top": 0.5,
                "bottom": 0.5,
            }

            for num in problem_nums:
                file.write(f"{num}\n")

            file.write("\n\n")

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
                solution_text_rgb=(127, 127, 127),
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

    """
    
    problem_nums = [
        770,
        807,
        815,
        220,
        317,
        429,
        579,
        598,
        723,
        766,
        773,
        818,
        64,
        161,
        177,
        199,
        223,
        245,
        248,
        257,
        298,
        322,
        332,
        342,
        390,
        427,
        446,
        455,
        471,
        479,
        486,
        506,
        513,
        531,
        561,
        576,
        615,
        619,
        624,
        633,
        641,
        664,
        748,
        870,
        255,
        411,
        730,
        895,
        716,
        325,
        597,
        437,
        309,
        706,
        56,
        527,
        202,
        671,
        729,
        678,
        504,
        42,
        765,
        375,
        338,
        287,
        496,
        425,
        200,
        859,
        894,
        68,
        649,
        40,
        179,
        379,
        438,
        451,
        84,
        418,
        331,
        396,
        107,
        217,
        116,
        53,
        720,
        445,
        772,
        155,
        848,
        611,
        871,
        878,
        781,
        443,
        464,
        430,
        515,
        54,
        556,
        734,
        246,
        787,
        743,
        764,
        30,
        630,
        476,
        209,
        864,
        225,
        869,
        459,
        110,
        658,
        393,
        291,
        327,
        187,
        120,
        638,
        537,
        206,
        119,
        113,
        759,
        643,
        407,
        213,
        656,
        400,
        683,
        733,
        274,
        584,
        707,
        587,
        46,
        359,
        31,
        63,
        583,
        754,
        222,
        12,
        36,
        596,
        687,
        114,
        450,
        755,
        502,
        82,
        823,
        302,
        426,
        170,
        104,
        5,
        421,
        366,
        482,
        616,
        328,
        372,
        548,
        59,
        96,
        144,
        172,
        644,
        166,
        397,
        761,
        875,
        398,
        775,
        802,
        726,
        549,
        83,
        221,
        123,
        344,
        888,
        201,
        844,
        570,
        526,
        461,
        566,
        645,
        879,
        849,
        368,
        456,
        382,
        162,
        747,
        111,
        480,
        853,
        347,
        749,
        108,
        571,
        528,
        165,
        568,
        448,
        118,
        780,
        176,
        15,
        208,
        410,
        554,
        863,
        535,
        335,
        243,
        562,
        229,
        782,
        713,
        582,
        639,
        577,
        146,
        363,
        346,
        319,
        813,
        791,
        128,
        796,
        542,
        877,
        147,
        628,
        215,
        665,
        790,
        271,
        684,
        61,
        744,
        484,
        698,
        284,
        804,
        792,
        264,
        623,
        320,
        77,
        34,
        184,
        751,
        798,
        816,
        210,
        25,
        880,
        16,
        629,
        321,
        269,
        574,
        140,
        169,
        728,
        691,
        409,
        655,
        308,
        663,
        599,
        149,
        93,
        550,
        846,
        3,
        675,
        841,
        233,
        237,
        612,
        580,
        279,
        156,
        288,
        362,
        138,
        622,
        740,
        704,
        610,
        899,
        505,
        364,
        196,
        171,
        651,
        661,
        732,
        626,
        76,
        378,
        592,
        608,
        440,
        449,
        491,
        267,
        280,
        6,
        143,
        889,
        541,
        709,
        668,
        845,
        667,
        47,
        565,
        27,
        180,
        503,
        483,
        530,
        81,
        401,
        357,
        313,
        674,
        517,
        758,
        348,
        329,
        405,
        762,
        227,
        862,
        824,
        26,
        457,
        627,
        292,
        768,
        692,
        392,
        886,
        316,
        603,
        834,
        422,
        497,
        672,
        67
    ]

    problem_selections = [(num, collection_name) for num in problem_nums]
    random.shuffle(problem_selections)

    margin_in = {
        "left": 0.5,
        "right": 0.5,
        "top": 0.5,
        "bottom": 0.5,
    }
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

    """



    

    # creates the booklet PDF. NEWEST

    margin_in = {
        "left": 0.25 + 1.5,  # 0.25 + 1.25,
        "right": 0.25 + 1.5,  # 0.25 + 1.25,
        "top": 0.25,
        "bottom": 0.25,
    }

    tsumego_pdf.create_pdf(
        problem_selections,
        (8.5 * 72, 5.5 * 72),
        margin_in=margin_in,
        color_to_play="black",
        landscape=True,
        num_columns=1,
        column_spacing_in=1,
        spacing_below_in=1 / 2,
        placement_method="proportional",
        include_text=True,
        problem_text_rgb=(255, 255, 255),
        solution_text_rgb=(255, 255, 255),#(127, 127, 127),
        include_page_num=False,
        display_width=11,
        draw_sole_solving_stone=True,
        verbose=True,  # shows progress bar
        is_booklet=True,
        num_signatures=3,
        booklet_cover="japanese",
        embed_cover_in_signatures=True,
        booklet_center_padding_in=1, # 1 1/4 --> 2 1/2
        ratio_to_flip_xy=7 / 12,
        outline_thickness_in=1/96,
        line_width_in=1/96,
        booklet_key_in_printers_spread=True,
        solution_mark="x",
    )"""

    elapsed = time.time() - start_time
    print(f"that took {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()
