from ultralytics import YOLO
import cv2
from stockfish import Stockfish

# Constants
FEN_MAPPING = {
    "black-pawn": "p", "black-rook": "r", "black-knight": "n", "black-bishop": "b", "black-queen": "q", "black-king": "k",
    "white-pawn": "P", "white-rook": "R", "white-knight": "N", "white-bishop": "B", "white-queen": "Q", "white-king": "K"
}
GRID_BORDER = 10  # Border size in pixels
GRID_SIZE = 204  # Effective grid size (10px to 214px)
BLOCK_SIZE = GRID_SIZE // 8  # Each block is ~25px
X_LABELS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']  # Labels for x-axis (a to h)
Y_LABELS = [8, 7, 6, 5, 4, 3, 2, 1]  # Reversed labels for y-axis (8 to 1)

# Functions
def get_grid_coordinate(pixel_x, pixel_y):
    """
    Function to determine the grid coordinate of a pixel, considering a 10px border and
    the grid where bottom-left is (a, 1) and top-left is (h, 8).
    """
    # Grid settings
    border = 10  # 10px border
    grid_size = 204  # Effective grid size (10px to 214px)
    block_size = grid_size // 8  # Each block is ~25px

    x_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']  # Labels for x-axis (a to h)
    y_labels = [8, 7, 6, 5, 4, 3, 2, 1]  # Reversed labels for y-axis (8 to 1)

    # Adjust pixel_x and pixel_y by subtracting the border (grid starts at pixel 10)
    adjusted_x = pixel_x - border
    adjusted_y = pixel_y - border

    # Check bounds
    if adjusted_x < 0 or adjusted_y < 0 or adjusted_x >= grid_size or adjusted_y >= grid_size:
        return "Pixel outside grid bounds"

    # Determine the grid column and row
    x_index = adjusted_x // block_size
    y_index = adjusted_y // block_size

    if x_index < 0 or x_index >= len(x_labels) or y_index < 0 or y_index >= len(y_labels):
        return "Pixel outside grid bounds"

    # Convert indices to grid coordinates
    x_index = adjusted_x // block_size  # Determine the column index (0-7)
    y_index = adjusted_y // block_size  # Determine the row index (0-7)

    # Convert row index to the correct label, with '8' at the bottom
    y_labeld = y_labels[y_index]  # Correct index directly maps to '8' to '1'
    x_label = x_labels[x_index]
    y_label = 8 - y_labeld + 1

    return f"{x_label}{y_label}"

def predict_next_move(fen, stockfish):
    """
    Predict the next move using Stockfish.
    """
    if stockfish.is_fen_valid(fen):
        stockfish.set_fen_position(fen)
    else:
        return "Invalid FEN notation!"

    best_move = stockfish.get_best_move()
    return f"The predicted next move is: {best_move}" if best_move else "No valid move found (checkmate/stalemate)."

# Main Logic
if __name__ == "__main__":
    # Initialize the YOLOv8 model
    model = YOLO("standard.pt")  # Replace with your trained model weights file

    # Load the image
    image_path = "image5.jpg"
    image = cv2.imread(image_path)
    image = cv2.resize(image, (224, 224))
    height, width, _ = image.shape
 
    # Initialize the board for FEN (empty rows represented by "8")
    board = [["8"] * 8 for _ in range(8)]

    # Run detection
    results = model.predict(source=image, save=False, save_txt=False, conf=0.25)

    # Extract predictions and map to FEN board
    for result in results[0].boxes:
        x1, y1, x2, y2 = result.xyxy[0].tolist()
        class_id = int(result.cls[0])
        class_name = model.names[class_id]

        # Convert class_name to FEN notation
        fen_piece = FEN_MAPPING.get(class_name, None)
        if not fen_piece:
            continue

        # Calculate the center of the bounding box
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        # Convert to integer pixel coordinates
        pixel_x = int(center_x)
        pixel_y = int(height - center_y)  # Flip Y-axis for generic coordinate system

        # Get grid coordinate
        grid_position = get_grid_coordinate(pixel_x, pixel_y)

        if grid_position != "Pixel outside grid bounds":
            file = ord(grid_position[0]) - ord('a')  # Column index (0-7)
            rank = int(grid_position[1]) - 1  # Row index (0-7)

            # Place the piece on the board
            board[7 - rank][file] = fen_piece  # Flip rank index for FEN

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

    position_fen = "/".join(fen_rows)

    # Ask the user for the next move side
    move_side = input("Enter the side to move (w for white, b for black): ").strip().lower()
    if move_side not in ["w", "b"]:
        print("Invalid input! Defaulting to 'w'.")
        move_side = "w"

    # Append the full FEN string continuation
    fen_notation = f"{position_fen} {move_side} - - 0 0"
    print(f"FEN Notation: {fen_notation}")

    # Initialize the Stockfish engine
    stockfish = Stockfish(
        path=r"D:\Projects\ChessVision\StockFish\stockfish\stockfish-windows-x86-64-avx2.exe",  # Replace with your Stockfish path
        depth=15,
        parameters={"Threads": 2, "Minimum Thinking Time": 30}
    )

    # Predict the next move
    next_move = predict_next_move(fen_notation, stockfish)
    print(next_move)
