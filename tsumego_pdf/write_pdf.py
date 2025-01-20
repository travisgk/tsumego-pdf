import os
import sys
import tempfile
import time
import pdf2image
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from tsumego_pdf.draw_game.board_graphics import DPI, draw_cover

_DRAW_PUNCH_HOLES = True  # only if printers spread is being used.
_PUNCH_HOLE_RGB = (128, 128, 128)
_PUNCH_HOLE_RADIUS_IN = 1 / 64
_PUNCH_HOLE_BEGIN_IN = 1 / 2
_NUM_PUNCH_HOLES = 6


def pdf_to_images(pdf_path):
    """
    Returns a list of temporary image paths which are the pages of the given PDF.
    """
    images = pdf2image.convert_from_path(pdf_path)

    temp_files = []
    for page_number, image in enumerate(images, start=1):
        # creates a temporary file.
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        image.save(temp_file.name, "PNG")
        temp_files.append(temp_file.name)

    return temp_files


def progress_bar(
    percent_done,
    est_seconds_left=None,
    prefix: str = "",
    length=50,
    fill="█",
    print_end="\r",
):
    """
    Prints a progress bar to the console.

    Parameters:
        total (int): total iterations or steps.
        est_seconds_left: the amount of seconds estimated to remain.
        length (int): length of the progress bar.
        fill (str): character to fill the progress bar.
        print_end (str): ending character (default is a carriage return).
    """
    if est_seconds_left is None:
        time_prefix = "        "
    else:
        seconds = round(est_seconds_left)
        minutes = seconds // 60
        hours = minutes // 60

        seconds = seconds % 60
        minutes = minutes % 60
        time_prefix = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    percent_done = max(0, percent_done)
    percent_done = min(1, percent_done)

    filled_length = int(length * percent_done) if percent_done != 0 else 0
    bar = fill * filled_length + "-" * (length - filled_length)
    sys.stdout.write(f"\r{prefix:<10} {time_prefix} |{bar}| {percent_done*100:.1f}%")
    sys.stdout.flush()
    sys.stdout.write(print_end)


def write_images_to_pdf(
    paths: list,
    out_path: str,
    paper_size,  # 72 DPI
    verbose: bool,  # if True, prints progress bar.
):
    start_time = time.time()
    out_pdf = canvas.Canvas(out_path, pagesize=paper_size)

    with Image.open(paths[0]) as img:
        img_w, img_h = img.size
    scale_x = paper_size[0] / img_w
    scale_y = paper_size[1] / img_h
    scale = min(scale_x, scale_y)

    out_w = img_w * scale
    out_h = img_h * scale

    num_pages = len(paths)

    for i, path in enumerate(paths):
        out_pdf.drawImage(path, 0, 0, width=out_w, height=out_h)
        if i < len(paths) - 1:
            out_pdf.showPage()

        percent_done = (i + 1) / num_pages
        elapsed = time.time() - start_time
        avg_duration = elapsed / (i + 1)
        remaining_processes = num_pages - (i + 1)
        est = remaining_processes * avg_duration

        if verbose:
            progress_bar(percent_done, est, prefix="2) Save")

    out_pdf.save()


def write_images_to_booklet_pdf(
    paths: list,
    out_path: str,
    paper_size,  # 72 DPI
    booklet_center_padding_in,
    printers_spread: bool,
    booklet_cover: str,
    embed_cover_in_signatures: bool,
    num_signatures: int = 1,
    verbose: bool = False,  # if True, prints progress bar.
):
    """
    Takes the given image paths and writes them to a booklet PDF.
    It can also output multiple PDFs for bookbinding with multiple signatures.
    """
    start_time = time.time()

    # copies paths.
    img_paths = paths[:]

    # gets image width and height in pixels.
    img_w = int((paper_size[0] / 72) * DPI)
    img_h = int((paper_size[1] / 72) * DPI)

    """
    Step 0) Generates resources.
    """
    temp_paths = []

    # generates the image pasted on the spines of signatures
    # to help in the process of bookbinding.
    punch_hole_image = None
    if _DRAW_PUNCH_HOLES:
        punch_hole_image = Image.new("RGB", (256, 256), (255, 255, 255))
        punch_draw = ImageDraw.Draw(punch_hole_image)
        punch_draw.ellipse((2, 2, 254, 254), fill=_PUNCH_HOLE_RGB)
        punch_hole_dim = int(_PUNCH_HOLE_RADIUS_IN * DPI * 2)
        punch_hole_image = punch_hole_image.resize(
            (int(punch_hole_dim), int(punch_hole_dim)),
            Image.Resampling.LANCZOS,
        )
        start_y = _PUNCH_HOLE_BEGIN_IN * DPI
        spacing_y = (img_h - start_y * 2) / (_NUM_PUNCH_HOLES - 1)
        holes_y = [start_y + i * spacing_y for i in range(_NUM_PUNCH_HOLES)]

    # generates the image that's pasted on blank pages
    # so that the printer doesn't ignore them when printing.
    # (some printers will skip entirely blank pages).
    dummy_image = Image.new("RGB", (30, 30), (255, 255, 255))
    dummy_draw = ImageDraw.Draw(dummy_image)
    dummy_draw.ellipse((2, 2, 28, 28), fill=(245, 245, 245))

    dummy_image = dummy_image.resize(
        (int(10), int(10)),
        Image.Resampling.LANCZOS,
    )

    with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
        dummy_temp_path = temp_file.name

    dummy_image.save(dummy_temp_path)
    temp_paths.append(dummy_temp_path)

    """
    Step 1) Creates cover page.
    """
    cover_path = None
    if booklet_cover is not None:
        # draws cover.
        cover_image = draw_cover(img_w, img_h, booklet_cover)
        with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
            temp_path = temp_file.name
        cover_image.save(temp_path)
        temp_paths.append(temp_path)
        cover_path = temp_path

    """
    Step 2) Embeds the cover page and back page directly in the first/last
            signatures if specified to do so.
    """
    cover_directly_embedded = False
    if (
        embed_cover_in_signatures
        and printers_spread
        and booklet_cover is not None
        and num_signatures > 1
    ):
        img_paths = [cover_path, None] + img_paths[:]
        cover_directly_embedded = True

    """
    Step 3) Determine the number of needed papers 
            and adds necessary blank pages.
    """
    count = len(img_paths)
    papers_needed = (count - 1) // 4 + 1
    num_total_pages = papers_needed * 4
    needed_blank_pages = num_total_pages - count

    # inserts blank pages.
    for _ in range(needed_blank_pages):
        img_paths.append(None)

    if (
        img_paths[-1] is not None
        and embed_cover_in_signatures
        and printers_spread
        and booklet_cover is not None
        and num_signatures > 1
    ):
        # ensures the back page is blank
        # if the cover/back page is directly embedded.
        img_paths.extend([None, None, None, None])
        count = len(img_paths)
        papers_needed = (count - 1) // 4 + 1
        num_total_pages = papers_needed * 4
        needed_blank_pages = num_total_pages - count

    """
    Step 4) Establishes the render order of pages per paper.
    """
    render_order = []
    papers_per_signature = None
    extra_papers = None
    if printers_spread:
        # determines the order using printers spread.
        papers_per_signature = papers_needed // num_signatures

        # the number of papers added to last signature.
        extra_papers = papers_needed - (papers_per_signature * num_signatures)

        for signature_i in range(num_signatures):
            # determines the pages displayed for each paper
            # by iterating through the number of signatures.
            start_page = signature_i * papers_per_signature * 4
            end_page = (((signature_i + 1) * papers_per_signature)) * 4 - 1
            if signature_i == num_signatures - 1:
                end_page += extra_papers * 4

            step = end_page - start_page + 1

            for i in range(start_page, start_page + step // 2):
                local_start = i - start_page
                if i % 2 == 0:
                    render_order.append((end_page - local_start, i, signature_i))
                else:
                    render_order.append((i, end_page - local_start, signature_i))

    else:
        # determines the order using normal digital display.
        render_order.append((num_total_pages - 1, 0, None))
        for i in range(1, num_total_pages - 1, 2):
            render_order.append((i, i + 1, None))

        if img_paths[num_total_pages - 1] is not None:
            render_order[0] = (None, 0, None)
            render_order.append((num_total_pages - 1, None, None))

    """
    Step 5) Opens PDF writers.
    """
    if (
        printers_spread
        and booklet_cover is not None
        and num_signatures > 1
        and not embed_cover_in_signatures
    ):
        cover_path = out_path[:-4] + "-cover.pdf"
        out_pdf = canvas.Canvas(cover_path, pagesize=paper_size)
    elif (
        printers_spread
        and num_signatures > 1
        and (booklet_cover is None or embed_cover_in_signatures)
    ):
        new_path = out_path[:-4] + f"-signature-0.pdf"
        out_pdf = canvas.Canvas(new_path, pagesize=paper_size)
    else:
        out_pdf = canvas.Canvas(out_path, pagesize=paper_size)

    scale_x = paper_size[0] / img_w
    scale_y = paper_size[1] / img_h
    scale = min(scale_x, scale_y)

    out_w = img_w * scale
    out_h = img_h * scale

    # adds booklet cover.
    if booklet_cover is not None and not cover_directly_embedded:
        out_pdf.drawImage(cover_path, out_w // 2, 0, width=out_w // 2, height=out_h)
        out_pdf.showPage()  # blank for double-sided cover.

        if printers_spread:
            out_pdf.drawImage(
                dummy_temp_path,
                ((img_w / 300 * 72) * 0.5) + 5,
                ((img_h / 300 * 72) * 0.5) - 5,
                width=10,
                height=10,
            )
            if num_signatures > 1:
                out_pdf.save()
                new_path = out_path[:-4] + f"-signature-0.pdf"
                out_pdf = canvas.Canvas(new_path, pagesize=paper_size)

            else:
                out_pdf.showPage()

    num_pages = len(render_order)
    last_signature_i = 0

    """
    Step 6) Writes the page images to the output PDFs.
    """
    for i, row in enumerate(render_order):
        left_element, right_element, signature_i = row
        if printers_spread and last_signature_i != signature_i and num_signatures > 1:
            out_pdf.save()
            last_signature_i = signature_i
            new_path = out_path[:-4] + f"-signature-{signature_i}.pdf"
            out_pdf = canvas.Canvas(new_path, pagesize=paper_size)

        left_path = None if left_element is None else img_paths[left_element]
        right_path = None if right_element is None else img_paths[right_element]

        left_image = Image.open(left_path) if left_path is not None else None
        right_image = Image.open(right_path) if right_path is not None else None

        page_image = Image.new("RGB", (img_w, img_h), (255, 255, 255))

        if not printers_spread and left_image is None and right_image is None:
            # entirely blank pages are skipped for digital output.
            continue

        if left_image is not None:
            page_paste_x = int(
                img_w / 2 - booklet_center_padding_in * DPI / 2 - left_image.size[0]
            )
            dpi_x = int(int(page_paste_x / DPI * 72) * (DPI / 72))
            page_image.paste(left_image, (dpi_x, 0))

        if right_image is not None:
            if right_path == cover_path:
                page_paste_x = img_w // 2
            else:
                page_paste_x = int(img_w / 2 + booklet_center_padding_in * DPI / 2)

            dpi_x = int(int(page_paste_x / DPI * 72) * (DPI / 72))
            page_image.paste(right_image, (dpi_x, 0))

        if left_image is None and right_image is None:
            out_pdf.drawImage(
                dummy_temp_path,
                ((img_w / 300 * 72) * 0.5) + 5,
                ((img_h / 300 * 72) * 0.5) - 5,
                width=10,
                height=10,
            )

        if _DRAW_PUNCH_HOLES and (
            (i < len(render_order) - 1 and render_order[i + 1][2] != signature_i)
            or i == len(render_order) - 1
        ):
            # draws punch holes for the center pages of each signature.
            paste_x = int(img_w / 2 - punch_hole_image.size[0] / 2)
            for hole_y in holes_y:
                paste_y = int(hole_y - punch_hole_image.size[1] / 2)
                page_image.paste(punch_hole_image, (paste_x, paste_y))

        with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
            temp_path = temp_file.name
        page_image.save(temp_path)
        temp_paths.append(temp_path)

        out_pdf.drawImage(temp_path, 0, 0, width=out_w, height=out_h)
        if i < len(render_order) - 1:
            out_pdf.showPage()

        # shows the user how much time is left to export the PDFs.
        percent_done = (i + 1) / num_pages
        elapsed = time.time() - start_time
        avg_duration = elapsed / (i + 1)
        remaining_processes = num_pages - (i + 1)
        est = remaining_processes * avg_duration

        if verbose:
            progress_bar(percent_done, est, prefix="2) Save")

    out_pdf.save()

    for path in temp_paths:
        os.remove(path)
