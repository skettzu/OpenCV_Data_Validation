import cv2
import numpy as np

def find_object_centers(frame, color_lower, color_upper):
    # Convert the frame to the HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Create a mask for the specified color range
    mask = cv2.inRange(hsv, color_lower, color_upper)
    
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    centers = []
    for cnt in contours:
        # Calculate the center of the contour
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            centers.append((cX, cY))
    
    return centers

def draw_centers_and_measure(frame, centers):
    if len(centers) >= 2:
        # Draw the center of each object
        for center in centers:
            cv2.circle(frame, center, 5, (255, 0, 0), -1)
        
        # Calculate and draw the line between centers
        cv2.line(frame, centers[0], centers[1], (0, 255, 0), 2)
        
        # Calculate the distance between the centers
        distance = np.linalg.norm(np.array(centers[0]) - np.array(centers[1]))
        cv2.putText(frame, f"Distance: {distance:.2f}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    return frame

# Define the lower and upper bounds of your object's color in HSV
# These values should be adjusted based on the color of your objects
color_lower = np.array([50, 100, 100])
color_upper = np.array([70, 255, 255])

# Start capturing video from the webcam
cap = cv2.VideoCapture(0)

while True:
    # Capture a single frame
    ret, frame = cap.read()
    if not ret:
        break
    
    # Find the centers of objects
    centers = find_object_centers(frame, color_lower, color_upper)
    
    # Draw the centers and measure the distance
    frame = draw_centers_and_measure(frame, centers)
    
    # Display the resulting frame
    cv2.imshow('Frame', frame)
    
    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close all windows
cap.release()
cv2.destroyAllWindows()