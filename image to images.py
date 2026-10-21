from PIL import Image
import os
import math


def resize_image(image_path, real_width, real_height, dpi):
    """
    Resize an image to real-life dimensions in inches, given the desired DPI.
    """
    img = Image.open(image_path)

    # Original size in inches
    original_width, original_height = img.size
    print(f"Original size: {original_width}x{original_height} pixels")
    print(f"Real-life size at {dpi} DPI: {original_width / dpi}x{original_height / dpi} inches")

    # Calculate new dimensions in pixels
    width_px = int(real_width * dpi)
    height_px = int(real_height * dpi)
    img_resized = img.resize((width_px, height_px), Image.Resampling.LANCZOS)
    return img_resized


def split_image(image, paper_width, paper_height, dpi, gutter_size):
    """
    Split the image into pieces that fit onto paper of the specified size.
    """
    paper_width_px = int(paper_width * dpi)
    paper_height_px = int(paper_height * dpi)
    gutter_px = int(gutter_size * dpi)

    img_width, img_height = image.size
    x_pieces = math.ceil(img_width / paper_width_px)
    y_pieces = math.ceil(img_height / paper_height_px)

    pieces = []
    for y in range(y_pieces):
        for x in range(x_pieces):
            left = x * paper_width_px - gutter_px
            top = y * paper_height_px - gutter_px
            right = (x + 1) * paper_width_px + gutter_px
            bottom = (y + 1) * paper_height_px + gutter_px

            # Ensure we don't go out of bounds
            left = max(left, 0)
            top = max(top, 0)
            right = min(right, img_width)
            bottom = min(bottom, img_height)

            piece = image.crop((left, top, right, bottom))
            pieces.append(piece)
    return pieces


def save_pieces(pieces, output_folder):
    """
    Save each piece as a separate image.
    """
    os.makedirs(output_folder, exist_ok=True)
    for i, piece in enumerate(pieces):
        piece.save(os.path.join(output_folder, f"piece_{i + 1}.png"))


# Parameters
image_path = r"D:\3. projects\2022 to now\11. eastie farms\Varietions\Easti farms 9 (final ver).png"
output_folder = r"D:\3. projects\2022 to now\11. eastie farms\Varietions\pieces"
real_width = 10  # inches
real_height = 12  # inches
paper_width = 8.5  # inches
paper_height = 11  # inches
dpi = 300  # printing resolution
gutter_size = 1  # inches

# Processing
image = resize_image(image_path, real_width, real_height, dpi)
pieces = split_image(image, paper_width, paper_height, dpi, gutter_size)
save_pieces(pieces, output_folder)

print(f"Image pieces saved in folder: {output_folder}")

