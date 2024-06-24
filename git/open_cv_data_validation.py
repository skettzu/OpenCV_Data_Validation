import cv2
import numpy as np
import math
import csv
import datetime
import time

'''
Disable all onboard cameras before running program
'''
'''
WARNING: When using this test script, please block the webcam from any bg bright colors using your body or have a white/black piece of paper to 
act as the background. Usage of a shadowbox/photobox is strongly encouraged for optimal performance.
It is recommended to wear black medical gloves as well if manually driving finger. Not following this recommendation may result in
inaccurate results.

** Closer the finger is to the camera, the more accurate the data
'''

'''
Notes:
Will be utilizing a different color sticker for each point of interest
Script will go through and create a mask for each point of interest
It will measure the distance between the center of the stickers (yellow to blue [top]) and (green to orange [bottom])
Angle will be calculated based on the distance from the center of the stickers and displayed on the top left corner of the frame
Law of Cosines will be used to calculate the angle

Will be using blue sticker instead of pink
'''
'''
To Do:
- Use shadowbox and motorized test setup to validate the angle calculations [prio]
- Debug why angle calc is running into an error, possibly related to the rate that perceived width is updated at [done]
- Measure the static distances between crevice and sticker center and replace placeholders [done]
- Create a test setup with external webcam for optimal results
- Sampling by maximum area instead may be more feasible as the sticker is smaller [just stick to current as will be in a controlled env]
- Validate color values are within range [green, yellow, blue, orange validated] [done] [will need to revalidate during actual measurement]
    - Most updated hsv values are in width_calc_test.py
- Enlarge webcam window for better visibility
'''
datetime_object = datetime.datetime.now()
datetime_string = datetime_object.strftime("%Y_%m_%d_%H_%M_%S")
print(datetime_string)
# File directory to store the csv file
file_path = fr"C:\Users\huangd8\Desktop\OpenCV\Data_Trial_{datetime_string}.csv"
# Angle data & timestamp to write to csv file
data = [['Top angle:'], ['Bottom angle:'], [' '], ['Timestamp:']]

# Define the minimum area for the objects to be detected
min_area = 10^2
max_area = 15^2

# Your known width or height of the object
KNOWN_WIDTH = 1.5875  # Width of sticker in millimeters (1/16 of inch)

# Your known distance from the camera to the object when calibrating
# KNOWN_DISTANCE = 230.0  # Distance from camera in millimeters

# Your known static distance of top joint crevice side in mm (orange side from diagram) [yellow sticker]
KNOWN_STATIC_TOP_DISTANCE1 = 7.0 # ~7 mm

# Your known static distance of top joint crevice side in mm (blue side from diagram) [blue sticker]
KNOWN_STATIC_TOP_DISTANCE2 = 9.5 # ~9.5 mm

# Your known static distance of top joint crevice side in mm (orange side from diagram) [green sticker]
KNOWN_STATIC_BOT_DISTANCE1 = 6.5 # ~6.5 mm
# Your known static distance of top joint crevice side in mm (blue side from diagram) [orange sticker]
KNOWN_STATIC_BOT_DISTANCE2 = 8.5 # ~8.5 mm

# The perceived width in pixels by OpenCV/Webcam
perceived_width = 0

# Define the lower and upper bounds of your object's color in HSV
# These values should be adjusted based on the color of your objects
color_lower_yellow = np.array([25, 70, 70])
color_upper_yellow = np.array([35, 255, 255])

# Is actually blue
color_lower_blue = np.array([110, 80, 80])
color_upper_blue = np.array([130, 255, 255])


color_lower_green = np.array([45, 80, 80])
color_upper_green = np.array([75, 255, 255])

color_lower_orange = np.array([10, 80, 0])
color_upper_orange = np.array([25, 255, 255])

# Start capturing video from the webcam
cap = cv2.VideoCapture(700)

# Centers for the points of interest
centers1 = []  # top
centers2 = []  # bottom

# Keep track of distances for average
#distance_sum = 0
#distance_num = 0

#focal_length = (perceived_width * KNOWN_DISTANCE) / KNOWN_WIDTH

def find_angles_and_display(frame, dist_yb, dist_go):
    print("find_angles_and_display called")
    top_angle = 0
    bot_angle = 0

    # Angle calculation and display onto frame

    # Calculate the perceived static distances between the center of the stickers and the center of the object
    perceived_top_dist1 = (KNOWN_STATIC_TOP_DISTANCE1/KNOWN_WIDTH)*perceived_width
    perceived_top_dist2 = (KNOWN_STATIC_TOP_DISTANCE2/KNOWN_WIDTH)*perceived_width
    perceived_bot_dist1 = (KNOWN_STATIC_BOT_DISTANCE1/KNOWN_WIDTH)*perceived_width
    perceived_bot_dist2 = (KNOWN_STATIC_BOT_DISTANCE2/KNOWN_WIDTH)*perceived_width
    

    # Calculate the top angle using law of cosines
    try:
        #top_angle = math.degrees(math.acos((dist_yb**2 - perceived_top_dist1**2 - perceived_top_dist2**2)/(-2*perceived_top_dist1*perceived_top_dist2)))
        top_angle = math.degrees(math.acos((50**2 - perceived_top_dist1**2 - perceived_top_dist2**2)/(-2*perceived_top_dist1*perceived_top_dist2)))
        # Display top angle onto the frame
        cv2.putText(frame, f"Top Angle: {top_angle:.4f}°", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        print("Top angle is ", top_angle)
    except ValueError:
        print("Error calculating top angle!\n")
    # Calculate the bottom angle using law of cosines
    try:
        #bot_angle = math.degrees(math.acos((dist_go**2 - perceived_bot_dist1**2 - perceived_bot_dist2**2)/(-2*perceived_bot_dist1*perceived_bot_dist2)))
        bot_angle = math.degrees(math.acos((50**2 - perceived_bot_dist1**2 - perceived_bot_dist2**2)/(-2*perceived_bot_dist1*perceived_bot_dist2)))
        # Display bottom angle onto the frame
        cv2.putText(frame, f"Bottom Angle: {bot_angle:.4f}°", (50,200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)    
        print("Bottom angle is ", bot_angle)
    except ValueError:
        print("Error calculating bottom angle!\n")
    timestamp = time.time() - start_time
    # Add data to csv
    data[0].append(top_angle)
    data[1].append(bot_angle)
    data[2].append(" ")
    data[3].append(timestamp)
def find_object_centers(cx, cy, cw, ch, joint):
    global centers1
    global centers2
    global prev_x1, prev_x2
    global prev_y1, prev_y2
    global perceived_width
    # Calculate the center coordinates of the rectangle
    center_x = int(cx + cw / 2)
    center_y = int(cy + ch / 2)

    # Constantly update perceived width
    perceived_width = cw
    # Find center for top objects
    if joint == 1:
        if centers1 == []:
            centers1.append((center_x, center_y))
            prev_x1 = center_x
            prev_y1 = center_y
        elif len(centers1) == 1:
            # Sort so it doesn't sample the same rectangle twice
            if((not (prev_x1 - 8 <= center_x <= prev_x1 + 8) and not (prev_y1 - 8 <= center_y <= prev_y1 + 8))):
                centers1.append((center_x, center_y))
        elif len(centers1) == 2:
            centers1 = []
    # Find center for bottom objects
    else:
        if centers2 == []:
            centers2.append((center_x, center_y))
            prev_x2 = center_x
            prev_y2 = center_y
        elif len(centers2) == 1:
            # Sort so it doesn't sample the same rectangle twice
            if((not (prev_x2 - 8 <= center_x <= prev_x2 + 8) and not (prev_y2 - 8 <= center_y <= prev_y2 + 8))):
                centers2.append((center_x, center_y))
        elif len(centers2) == 2:
            centers2 = []

def draw_centers_and_measure(frame, centers, joint):
    global centers1, centers2
    distance_pixels = 0
    #global distance_sum
    #global distance_num
    if len(centers) >= 2:
        # Draw the center of each object
        for center in centers:
            cv2.circle(frame, center, 2, (255, 0, 0), -1)
        
        # Calculate and draw the line between centers
        cv2.line(frame, centers[0], centers[1], (0, 255, 0), 2)
        
        # Calculate the distance between the centers
        distance_pixels = np.linalg.norm(np.array(centers[0]) - np.array(centers[1]))
        distance_mm = distance_pixels * (KNOWN_WIDTH/perceived_width)
        #distance_sum = distance_sum + distance_mm
        #distance_num = distance_num + 1
        if joint == 1:
            cv2.putText(frame, f"Top Distance: {distance_mm:.2f}mm", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            centers1 = []
        else:
            cv2.putText(frame, f"Bottom Distance: {distance_mm:.2f}mm", (50,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            centers2 = []
    return frame, distance_pixels

if __name__ == "__main__":
    global start_time 
    start_time = time.time()
    dist_yb = 0
    dist_go = 0
    while True:
        # Capture a single frame
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert the frame to the HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a mask for the specified color range (yellow, blue, green, and orange)
        yellow_mask = cv2.inRange(hsv, color_lower_yellow, color_upper_yellow)
        blue_mask = cv2.inRange(hsv, color_lower_blue, color_upper_blue)
        green_mask = cv2.inRange(hsv, color_lower_green, color_upper_green)
        orange_mask = cv2.inRange(hsv, color_lower_orange, color_upper_orange)

        # Combine the masks into a single mask
        combined_mask1 = cv2.bitwise_or(yellow_mask, blue_mask)
        compiled_mask2 = cv2.bitwise_or(green_mask, orange_mask)


        # Find contours in the image
        contours_yb, _ = cv2.findContours(combined_mask1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_go, _ = cv2.findContours(compiled_mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Just to test UI placement
        '''
        top_angle = 35
        bot_angle = 50
        cv2.putText(frame, f"Top Angle: {top_angle:.2f}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(frame, f"Bottom Angle: {bot_angle:.2f}", (50,200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        '''
        distance_mm = 2
        cv2.putText(frame, f"Top Distance: {distance_mm:.2f}mm", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        # distance_mm = 3
        # cv2.putText(frame, f"Bottom Distance: {distance_mm:.2f}mm", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        # Just to test UI placement

        # Test for csv writing
        #data[0].append("35")
        #data[1].append("50")

        # Go through and find the distances between the centers of the objects (yellow and blue), (green and orange)
        for contour in contours_yb:
            area = cv2.contourArea(contour)
            if ((area > min_area) and (area < max_area)):
                # Object is larger than minimum area, so proceed with distance calculation
                # Assuming you have the perceived width in pixels (e.g., from bounding box width)
                x, y, w, h = cv2.boundingRect(contour)
                perceived_width = w  # or use h for height, depending on known dimension
                
                # Draw the bounding box for visualization
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Find the centers of objects
                find_object_centers(x, y, w, h, 1)
                # Draw the centers and measure the distance
                frame, dist_yb = draw_centers_and_measure(frame, centers1, 1)
                print(centers1)
                print(prev_x1)
                print(prev_y1)
                print("yb countour detected")
        for contour in contours_go:
            area = cv2.contourArea(contour)
            if ((area > min_area) and (area < max_area)):
                # Object is larger than minimum area, so proceed with distance calculation
                # Assuming you have the perceived width in pixels (e.g., from bounding box width)
                x, y, w, h = cv2.boundingRect(contour)
                perceived_width = w  # or use h for height, depending on known dimension
                
                # Draw the bounding box for visualization
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Find the centers of objects
                find_object_centers(x, y, w, h, 2)
                # Draw the centers and measure the distance
                frame, dist_go = draw_centers_and_measure(frame, centers2, 2)
                print(centers2)
                print(prev_x2)
                print(prev_y2)
        if dist_yb <= 50 and dist_go <= 50:
            # Calculate and display the angles of each joint on the frame
            find_angles_and_display(frame, dist_yb, dist_go)
        # Display the resulting frame
        cv2.imshow('Frame', frame)
        
        # Exit the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            #avg_distance = distance_sum/distance_num
            #print(f"Average Distance is {avg_distance:.2f} from {distance_num} data points")
            # Open file and create writer object
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(list(zip(*data)))
            break

    # Release the capture and close all windows
    cap.release()
    cv2.destroyAllWindows()