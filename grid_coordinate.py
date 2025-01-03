def get_grid_coordinate(pixel_x, pixel_y):

    # Grid settings
    border = 10  # 10px border
    grid_size = 204  # Effective grid size (from 10px to 214px)
    block_size = grid_size // 8  # Each block is approximately 25px
    
    x_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']  # Labels for x-axis
    y_labels = [8, 7, 6, 5, 4, 3, 2, 1]  # Labels for y-axis

    # Adjust coordinates by subtracting the border
    adjusted_x = pixel_x - border
    adjusted_y = pixel_y - border

    # Check if the pixel is within bounds
    if adjusted_x < 0 or adjusted_y < 0 or adjusted_x >= grid_size or adjusted_y >= grid_size:
        return "Pixel outside grid bounds"

    # Determine the column and row indices
    x_index = adjusted_x // block_size
    y_index = adjusted_y // block_size

    # Map indices to grid labels
    y_labeld = y_labels[y_index]  
    x_label = x_labels[x_index]
    y_label = 8 - y_labeld + 1

    return f"{x_label}{y_label}"
