import cv2
import numpy as np
from ultralytics import YOLO

def process_image(image_path):
    def shift_outward(corner, center, distance):
        vector = corner - center
        normalized_vector = vector / np.linalg.norm(vector)
        shifted_corner = corner + normalized_vector * distance
        return shifted_corner

    def rotate_points(points, rotation_matrix):
        """ Rotate the bounding box corners using the rotation matrix """
        return cv2.transform(np.array([points]), rotation_matrix)[0]

    # Load YOLO models
    bbox_model = YOLO("best.pt")
    segmentation_model = YOLO("segmentation.pt")

    # Load the input image
    image = cv2.imread(image_path)

    # Resize the image to 256x256
    image = cv2.resize(image, (256, 256))

    # Detect objects using `best.pt`
    bbox_results = bbox_model(image)
    bounding_boxes = []
    for result in bbox_results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id = int(box.cls[0])
            class_name = bbox_model.names[class_id]
            bounding_boxes.append((x1, y1, x2, y2, class_id, class_name))

    # Detect chessboard using `segmentation.pt`
    segmentation_results = segmentation_model(image)
    segmentation_mask = segmentation_results[0].masks.data.cpu().numpy().astype(np.uint8)[0]

    # Resize segmentation mask to match image dimensions
    segmentation_mask_resized = cv2.resize(segmentation_mask, (image.shape[1], image.shape[0]))

    # Find chessboard contour
    contours, _ = cv2.findContours(segmentation_mask_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("Chessboard contour not found.")
        return None, None

    largest_contour = max(contours, key=cv2.contourArea)
    epsilon = 0.02 * cv2.arcLength(largest_contour, True)
    approx_corners = cv2.approxPolyDP(largest_contour, epsilon, True)

    if len(approx_corners) != 4:
        print("Chessboard corners not detected correctly.")
        return None, None

    # Shift corners outward
    approx_corners = np.array(sorted(approx_corners[:, 0], key=lambda x: (x[1], x[0])), dtype=np.float32)
    center = np.mean(approx_corners, axis=0)

    top_leftcorner = 10
    top_rightcorner = 10
    bottom_rightcorner = 10
    bottom_leftcorner = 10

    shifted_top_left = shift_outward(approx_corners[0], center, top_leftcorner)
    shifted_top_right = shift_outward(approx_corners[1], center, top_rightcorner)
    shifted_bottom_right = shift_outward(approx_corners[2], center, bottom_rightcorner)
    shifted_bottom_left = shift_outward(approx_corners[3], center, bottom_leftcorner)

    shifted_corners = np.array([shifted_top_left, shifted_top_right, shifted_bottom_right, shifted_bottom_left], dtype=np.float32)

    # **Rotate the image before perspective transformation**
    image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # Adjust shifted corners for the rotated image
    h, w = image.shape[:2]
    rotation_matrix = cv2.getRotationMatrix2D((w / 2, h / 2), 90, 1)
    shifted_corners = rotate_points(shifted_corners, rotation_matrix)

    # Rotate bounding boxes
    rotated_boxes = []
    for box in bounding_boxes:
        x1, y1, x2, y2, class_id, class_name = box
        box_corners = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], dtype=np.float32)
        rotated_corners = rotate_points(box_corners, rotation_matrix)
        x_min, y_min = rotated_corners.min(axis=0)
        x_max, y_max = rotated_corners.max(axis=0)
        rotated_boxes.append((int(x_min), int(y_min), int(x_max), int(y_max), class_id, class_name))

    # Perspective transformation
    width, height = 256, 256
    destination_points = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype=np.float32)
    matrix = cv2.getPerspectiveTransform(shifted_corners, destination_points)
    warped_image = cv2.warpPerspective(image, matrix, (width, height))

    # Rotate the warped image (to match the original rotation)
      # Rotate back to original

    # Transform rotated bounding boxes using perspective matrix
    transformed_boxes = []
    for box in rotated_boxes:
        x1, y1, x2, y2, class_id, class_name = box
        corners = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], dtype=np.float32)
        transformed_corners = cv2.perspectiveTransform(np.array([corners]), matrix)[0]
        x_min, y_min = transformed_corners.min(axis=0)
        x_max, y_max = transformed_corners.max(axis=0)
        transformed_boxes.append((int(x_min), int(y_min), int(x_max), int(y_max), class_id, class_name))

    # Save the rotated warped image with bounding boxes
    cv2.imwrite('output/warped_image_with_boxes_rotated.jpg', warped_image)
    return warped_image, transformed_boxes
