from process_image import process_image
from grid_coordinate import get_grid_coordinate
from fen_generator import generate_fen

# Load the input image
image_path = "image.png"
warped_image, transformed_boxes = process_image(image_path)

if warped_image is not None and transformed_boxes is not None:
    fen_notation = generate_fen(warped_image, transformed_boxes)
    print(f"FEN Notation: {fen_notation}")
else:
    print("Failed to process the image.")
