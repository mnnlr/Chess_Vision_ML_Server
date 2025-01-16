# AI Powered Chess Analysis
Analyze chessboard states from images and predict optimal moves. By combining YOLO for object detection, FEN (Forsyth-Edwards Notation) for board state representation, and Stockfish for move prediction, this system provides a seamless experience for chess enthusiasts and developers.

## Features

- ChessPieces Detection: Uses YOLO to detect chessboard positions accurately.
- State Representation: Automatically converts board positions into FEN format.
- Move Prediction: Leverages Stockfish to suggest the best move based on the input.
- Real-Time Processing: Optimized for fast and efficient performance.


## Getting Started

### Prerequisites

Ensure you have the following installed:
- Python 3.8+
- Required Python packages (see [requirements.txt](requirements.txt))
- YOLO pre-trained weights
- Stockfish (latest version recommended)


### Usage

1. Run the main script with an input image:
   ```bash
   python main.py --image path/to/chessboard.jpg


## Acknowledgments

- [YOLO](https://github.com/ultralytics/yolov5) for chessboard detection.
- [Stockfish](https://stockfishchess.org/) for move predictions.
- Chess community for inspiration and resources.
