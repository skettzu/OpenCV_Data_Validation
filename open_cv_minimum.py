import cv2
import numpy as np

# Initialize your webcam feed
cap = cv2.VideoCapture(0)

# Define the minimum area for the objects to be detected (you can adjust this value)
min_area = 300

# Your known width or height of the object
KNOWN_WIDTH = 19  # example value in some unit of measure

# Your known distance from the camera to the object when calibrating
KNOWN_DISTANCE = 240.0  # example value in the same unit of measure

focal_length = (58 * KNOWN_DISTANCE) / KNOWN_WIDTH
# Function to calculate distance from camera to object
def calculate_distance(focal_length, perceived_width, known_width):
    return (known_width * focal_length) / perceived_width

# Calculate the camera's focal length (call this once at the start, with known distance and known width)
# focal_length = (perceived_width_in_pixels * KNOWN_DISTANCE) / KNOWN_WIDTH

color_lower = np.array([25, 100, 100])
color_upper = np.array([35, 255, 255])

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert the frame to the HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the specified color range
    mask = cv2.inRange(hsv, color_lower, color_upper)

    # Find contours in the image
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            # Object is larger than minimum area, so proceed with distance calculation
            # Assuming you have the perceived width in pixels (e.g., from bounding box width)
            x, y, w, h = cv2.boundingRect(contour)
            perceived_width = w  # or use h for height, depending on known dimension
            
            # Draw the bounding box for visualization
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Calculate the distance to the object
            distance = calculate_distance(focal_length, perceived_width, KNOWN_WIDTH)
            
            # Display the distance on the frame
            cv2.putText(frame, f"{distance:.2f}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow('Frame', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()