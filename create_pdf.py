def png_to_pdf(
    images: list, pdf_path: str, page_size, landscape: bool=False
):
    if landscape:
        page_size = (max(page_size), min(page_size))
    else:
        page_size = (min(page_size), max(page_size))

    c = canvas.Canvas(pdf_path, pagesize=page_size)

    # creates a PDF canvas.
    pdf_width, pdf_height = page_size

    paths = []
    for i, image in enumerate(images):
        TEMP_PATH = f"temp-image-{i:03d}.png"
        paths.append(TEMP_PATH)
        img_width, img_height = image.size

        # calculates the scale factor to fit the image in the PDF.
        scale_x = pdf_width / img_width
        scale_y = pdf_height / img_height
        scale = min(scale_x, scale_y)

        image.save(TEMP_PATH)

        # scales the image and draw it on the PDF.
        c.drawImage(TEMP_PATH, 0, 0, width=img_width * scale, height=img_height * scale)
        
        if i < len(images) - 1:
            c.showPage()

    # saves the PDF.
    c.save()

    for path in paths:
        os.remove(path)