from grid_coordinate import get_grid_coordinate

def generate_fen(warped_image, transformed_boxes):
    """
    Generate FEN notation from warped chessboard image and bounding boxes.
    Args:
    - warped_image: Perspective-transformed chessboard image (not used here, kept for context).
    - transformed_boxes: List of bounding boxes with class IDs and coordinates.

    Returns:
    - FEN notation as a string.
    """
    fen_mapping = {
        "black-pawn": "p", "black-rook": "r", "black-knight": "n", "black-bishop": "b",
        "black-queen": "q", "black-king": "k", "white-pawn": "P", "white-rook": "R",
        "white-knight": "N", "white-bishop": "B", "white-queen": "Q", "white-king": "K"
    }

    # Initialize the board with empty rows
    board = [["8"] * 8 for _ in range(8)]

    for box in transformed_boxes:
        # Unpack bounding box data
        x1, y1, x2, y2, class_id, class_name = box  # Ensure transformed_boxes include class_name and coordinates

        # Map class name to FEN symbol
        fen_piece = fen_mapping.get(class_name, None)
        if not fen_piece:
            continue

        # Calculate the center of the bounding box
        center_x = (x1 + x2) / 2
        center_y = y2

        # Get grid coordinate
        pixel_x = int(center_x)
        pixel_y = int(center_y)
        grid_position = get_grid_coordinate(pixel_x, pixel_y)

        if grid_position != "Pixel outside grid bounds":
            file = ord(grid_position[0]) - ord('a')
            rank = int(grid_position[1]) - 1
            board[7 - rank][file] = fen_piece

    # Generate the FEN string
    fen_rows = []
    for row in board:
        fen_row = ""
        empty_count = 0
        for cell in row:
            if cell == "8":
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += cell
        if empty_count > 0:
            fen_row += str(empty_count)
        fen_rows.append(fen_row)

    return "/".join(fen_rows)
