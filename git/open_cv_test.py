import cv2
import numpy as np
import time
# Define the minimum area for the objects to be detected
min_area = 67^2

# Your known width or height of the object
KNOWN_WIDTH = 19.05  # Width of sticker in millimeters

# Your known distance from the camera to the object when calibrating
KNOWN_DISTANCE = 230.0  # Distance from camera in millimeters

# The perceived width in pixels by OpenCV
perceived_width = 0

# Keep track of distances for average
distance_sum = 0
distance_num = 0

#focal_length = (perceived_width * KNOWN_DISTANCE) / KNOWN_WIDTH

centers = []
prev_x = 0
prev_y = 0

def find_object_centers(cx, cy, cw, ch):
    global centers
    global prev_x
    global prev_y
    global perceived_width
    # Calculate the center coordinates of the rectangle
    center_x = int(cx + cw / 2)
    center_y = int(cy + ch / 2)

    # Constantly update perceived width
    perceived_width = cw
    if centers == []:
        centers.append((center_x, center_y))
        prev_x = center_x
        prev_y = center_y
    elif len(centers) == 1:
        # Sort so it doesn't sample the same rectangle twice
        if((not (prev_x - 30 <= center_x <= prev_x + 30) and not (prev_y - 30 <= center_y <= prev_y + 30))):
            centers.append((center_x, center_y))
    elif len(centers) == 2:
        centers = [] 

def draw_centers_and_measure(frame, centers):
    global distance_sum
    global distance_num
    if len(centers) >= 2:
        # Draw the center of each object
        for center in centers:
            cv2.circle(frame, center, 2, (255, 0, 0), -1)
        
        # Calculate and draw the line between centers
        cv2.line(frame, centers[0], centers[1], (0, 255, 0), 2)
        
        # Calculate the distance between the centers
        distance_pixels = np.linalg.norm(np.array(centers[0]) - np.array(centers[1]))
        distance_mm = distance_pixels * (KNOWN_WIDTH/perceived_width)
        distance_sum = distance_sum + distance_mm
        distance_num = distance_num + 1
        cv2.putText(frame, f"Distance: {distance_mm:.2f}mm", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        centers = []
    
    return frame

# Define the lower and upper bounds of your object's color in HSV
# These values should be adjusted based on the color of your objects
color_lower = np.array([25, 100, 100])
color_upper = np.array([35, 255, 255])

# Start capturing video from the webcam
cap = cv2.VideoCapture(0)

while True:
    # Capture a single frame
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert the frame to the HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the specified color range
    mask = cv2.inRange(hsv, color_lower, color_upper)

    # Find contours in the image
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            # Object is larger than minimum area, so proceed with distance calculation
            # Assuming you have the perceived width in pixels (e.g., from bounding box width)
            x, y, w, h = cv2.boundingRect(contour)
            perceived_width = w  # or use h for height, depending on known dimension
            
            # Draw the bounding box for visualization
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Find the centers of objects
            find_object_centers(x, y, w, h)
            # Draw the centers and measure the distance
            frame = draw_centers_and_measure(frame, centers)
            print(centers)
            print(prev_x)
            print(prev_y)
    # Display the resulting frame
    cv2.imshow('Frame', frame)
    
    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        avg_distance = distance_sum/distance_num
        print(f"Average Distance is {avg_distance:.2f} from {distance_num} data points")
        break

# Release the capture and close all windows
cap.release()
cv2.destroyAllWindows()