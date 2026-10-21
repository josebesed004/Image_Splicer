from PIL import Image
import os
import math
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import ghostscript
import os

def resize_image(image_path, real_width, dpi, printer_scale):
    """
    Resize an image to real-life dimensions in inches, given the desired DPI.
    The height is scaled proportionally based on the original aspect ratio of the image.
    """
    img = Image.open(image_path)
    original_width, original_height = img.size
    aspect_ratio = original_height / original_width  # Calculate aspect ratio

    real_height = real_width * aspect_ratio  # Scale height proportionally
    width_px = int(real_width * dpi * ( 100/printer_scale) ) # 100/printer scale is to account for the downscaling of the printer
    height_px = int(real_height * dpi * ( 100/printer_scale))
    img_resized = img.resize((width_px, height_px), Image.Resampling.LANCZOS) #what does the image resampling do here?

    print(f"\nOriginal size: {original_width}x{original_height} pixels")
    print(f"New size: {width_px}x{height_px} pixels (accounting for printer scaling)")
    print(f"Real-world size: {real_width}x{real_height} inches")

    return img_resized, real_height

def split_image(image, paper_width, paper_height, dpi, gutter_size):
    """
    Split the image into pieces that fit onto paper of the specified size,
    accounting for gutters as overlaps between pieces only (no gutter added to edges).
    """
    paper_width_px = int(paper_width * dpi)
    paper_height_px = int(paper_height * dpi)
    gutter_px = int(gutter_size * dpi)

    img_width, img_height = image.size

    # Calculate the number of pieces, factoring in gutter overlap
    x_pieces = math.ceil((img_width + gutter_px) / (paper_width_px - gutter_px))
    y_pieces = math.ceil((img_height + gutter_px) / (paper_height_px - gutter_px))

    pieces = []
    for y in range(y_pieces):
        for x in range(x_pieces):
            # Calculate crop coordinates with gutter overlap
            left = x * (paper_width_px - gutter_px)
            top = y * (paper_height_px - gutter_px)
            right = left + paper_width_px
            bottom = top + paper_height_px

            # Ensure coordinates are within the original image boundaries
            left = max(0, left)
            top = max(0, top)
            right = min(img_width, right)
            bottom = min(img_height, bottom)

            # Avoid invalid pieces
            if right <= left or bottom <= top:
                print(f"Skipping invalid piece: left={left}, top={top}, right={right}, bottom={bottom}")
                continue

            # Crop the piece
            piece = image.crop((left, top, right, bottom))
            pieces.append(piece)

    return pieces

def save_pieces_to_pdf(pieces, output_pdf, paper_width, paper_height, dpi, CMYK, printer_scale):
    """
    Save each piece as a page in a PDF, applying printer downscaling and using the specified paper dimensions.
    Convert temporary images to CMYK before adding them to the PDF.
    """
    # Convert paper dimensions from inches to points
    paper_width_pts = paper_width * 72
    paper_height_pts = paper_height * 72

    pdf_canvas = canvas.Canvas(output_pdf, pagesize=(paper_width_pts, paper_height_pts))

    for i, piece in enumerate(pieces):
        piece_width, piece_height = piece.size

        # Apply printer scaling to simulate downscaling
        scaled_width_px = int(piece_width * (printer_scale / 100))
        scaled_height_px = int(piece_height * (printer_scale / 100))

        # Resize the piece to simulate printer scaling
        piece_scaled = piece.resize((scaled_width_px, scaled_height_px), Image.Resampling.LANCZOS)

        # Convert pixels to points for placement in the PDF
        scale_width_pts = scaled_width_px / dpi * 72
        scale_height_pts = scaled_height_px / dpi * 72

        # Center the image on the page
        x_offset = (paper_width_pts - scale_width_pts) / 2
        y_offset = (paper_height_pts - scale_height_pts) / 2

        # Convert the piece to CMYK before saving
        if CMYK:
            piece_cmyk = piece_scaled.convert("CMYK")
        else:
            piece_cmyk = piece_scaled

        # Save the CMYK piece as a temporary JPEG file
        temp_file = f"temp_page_{i + 1}.jpg"
        piece_cmyk.save(temp_file, "JPEG")

        # Add the image to the PDF
        pdf_canvas.drawImage(temp_file, x_offset, y_offset, width=scale_width_pts, height=scale_height_pts)
        pdf_canvas.showPage()

        # Remove the temporary file
        os.remove(temp_file)

    pdf_canvas.save()

# Parameters
image_path = input("\nWhats the image path? - ").replace("\"", "").replace("\''", "")
output_pdf = input("Whats the folder path? - ").replace("\"", "").replace("\''", "")
pdf_name = input("How would you like to name the file? - ")
output_pdf_CMYK = output_pdf + f"\\{pdf_name}_CMYK.pdf"
output_pdf = output_pdf + f"\\{pdf_name}.pdf"
print(output_pdf)
printer_scale = int(input("Whats your printers print scale ex 95% (only the numbers please) - "))

real_width = float(input("What width? - "))  # inches
CMYK = bool(input("Want to convert to CMYK? (True or False)- "))
paper_width = 8.5  # inches
paper_height = 11  # inches
dpi = 300  # printing resolution
gutter_size = 1  # inches

# processing
try:
    image, real_height = resize_image(image_path, real_width, dpi, printer_scale)
    print(f"\nProportional height calculated as: {real_height:.2f} inches")
    pieces = split_image(image, paper_width, paper_height, dpi, gutter_size)
    save_pieces_to_pdf(pieces, output_pdf, paper_width, paper_height, dpi, CMYK, printer_scale)
    print(f"PDF saved successfully at: {output_pdf}")
except Exception as e:
    print(f"\nAn error occurred: {e}")