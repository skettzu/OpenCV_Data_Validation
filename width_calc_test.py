import cv2
import numpy as np

# Function to find the perceived width of the object of interest
def find_perceived_width(image, color_lower, color_upper):
    # Convert the image to the HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Create a mask for the specified color range
    mask = cv2.inRange(hsv, color_lower, color_upper)
    
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # If at least one contour was found
    if contours:
        # Find the largest contour, assumed to be the object of interest
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Calculate the bounding rectangle for the largest contour
        x, y, width, height = cv2.boundingRect(largest_contour)
        
        # Create a copy of the image to draw on
        color_image = image.copy()
        
        # Draw the bounding rectangle on the image
        cv2.rectangle(color_image, (x, y), (x + width, y + height), (0, 255, 0), 2)
        
        # Display the image with the bounding rectangle
        cv2.imshow('Bounding Rectangle', color_image)
        
        # Return the perceived width in pixels
        return width
    else:
        # No contours found, return None for width
        return None

# Define the lower and upper bounds of the object's color in HSV
# Adjust these values based on the color of your object
color_lower = np.array([25, 100, 100])
color_upper = np.array([35, 255, 255])

# Load your image
#image = cv2.imread('open_cv_test5.jpg')

# Initialize your webcam feed
cap = cv2.VideoCapture(0)
# Assuming your image was loaded correctly
while True:
    ret, frame = cap.read()
    if not ret:
        break
if image is not None:
    # Find the perceived width of the object
    width = find_perceived_width(image, color_lower, color_upper)
    
    if width is not None:
        print("Perceived Width in pixels:", width)
    else:
        print("Object not found")
    
    # Wait for a key press and close all windows
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Could not open or find the image")