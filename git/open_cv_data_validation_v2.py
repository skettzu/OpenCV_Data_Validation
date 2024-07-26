import cv2
import numpy as np
import math
import csv
import datetime
import time
import threading

'''
Version 2 samples two colors instead of four
'''
'''
** Closer the finger is to the camera, the more accurate the data
** If camera is not detecting a sticker vibrate the base a little bit to have it latch
'''

'''
To Do:
- Use shadowbox and motorized test setup to validate the angle calculations [prio]
- Find a consistent HSV range for colors [prio]
'''

# Actual static angles:
# top: 112 degrees
# bot: 104.5 degrees
datetime_object = datetime.datetime.now()
datetime_string = datetime_object.strftime("%Y_%m_%d_%H_%M_%S")
print(datetime_string)
# File directory to store the csv file
file_path = fr"C:\Users\huangd8\Desktop\OpenCV\Data_Trial_{datetime_string}.csv"
# Angle data & timestamp to write to csv file
data = [['Top angle:'], ['Bottom angle:'], [' '], ['Timestamp:']]

# Define the minimum & maximum area for the objects to be detected
min_area = 38
max_area = 68

# Your known width or height of the object
KNOWN_WIDTH = 1.5875  # Width of sticker in millimeters (1/16 of inch)

# Your known distance from the camera to the object when calibrating
# KNOWN_DISTANCE = 230.0  # Distance from camera in millimeters

# The longer the smaller the angle, the shorter the bigger the angle

# Your known static distance of top joint crevice side in mm (orange side from diagram) [yellow sticker]
KNOWN_STATIC_TOP_DISTANCE1 = 6.1 # ~6.5 mm

# Your known static distance of top joint crevice side in mm (blue side from diagram) [pink sticker]
KNOWN_STATIC_TOP_DISTANCE2 = 9 # ~9.5 mm

# Your known static distance of top joint crevice side in mm (orange side from diagram) [green sticker]
KNOWN_STATIC_BOT_DISTANCE1 = 6.3 # ~6.5 mm
# Your known static distance of top joint crevice side in mm (blue side from diagram) [orange sticker]
KNOWN_STATIC_BOT_DISTANCE2 = 8.2 # ~8.5 mm

# Initialize or and yel distances
dist_or = 0
dist_yel = 0
# Initialize top and bottom angles
top_angle = 0
bot_angle = 0

# The perceived width in pixels by OpenCV/Webcam
perceived_width = 0

# total angle sampled
total_angle = 0
sum_angle_top = 0
sum_angle_bot = 0

# Define the lower and upper bounds of your object's color in HSV
# These values should be adjusted based on the color of your objects
color_lower_yellow = np.array([23, 90, 90])
color_upper_yellow = np.array([40, 255, 255])

color_lower_orange = np.array([10, 105, 105])
color_upper_orange = np.array([22, 255, 255])

# Start capturing video from the webcam
cap = cv2.VideoCapture(1400)

# Centers for the points of interest
centers1 = []  # top
centers2 = []  # bottom

# Semaphore for sync (max one thread)
sem = threading.Semaphore(1)

#focal_length = (perceived_width * KNOWN_DISTANCE) / KNOWN_WIDTH

def find_angles_and_display(frame, dist_yel, dist_or):
    #print("find_angles_and_display called")
    global top_angle, bot_angle, total_angle, sum_angle_bot, sum_angle_top
    # Angle calculation and display onto frame

    # Calculate the perceived static distances between the center of the stickers and the center of the object
    perceived_top_dist1 = (KNOWN_STATIC_TOP_DISTANCE1/KNOWN_WIDTH)*perceived_width
    perceived_top_dist2 = (KNOWN_STATIC_TOP_DISTANCE2/KNOWN_WIDTH)*perceived_width
    perceived_bot_dist1 = (KNOWN_STATIC_BOT_DISTANCE1/KNOWN_WIDTH)*perceived_width
    perceived_bot_dist2 = (KNOWN_STATIC_BOT_DISTANCE2/KNOWN_WIDTH)*perceived_width
    
    if(perceived_top_dist1 and perceived_bot_dist1 and perceived_top_dist2 and perceived_bot_dist2 != 0):
        # Calculate the top angle using law of cosines
        if dist_yel != 0:
            try:
                top_angle = math.degrees(math.acos((dist_yel**2 - perceived_top_dist1**2 - perceived_top_dist2**2)/(-2*perceived_top_dist1*perceived_top_dist2)))
                #top_angle = math.degrees(math.acos((50**2 - perceived_top_dist1**2 - perceived_top_dist2**2)/(-2*perceived_top_dist1*perceived_top_dist2)))
                # Display top angle onto the frame
                #cv2.putText(frame, f"Top Angle: {top_angle:.4f}°", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                #print("Top angle is ", top_angle)
                # Reset top dists
                perceived_top_dist1 = 0
                perceived_top_dist2 = 0
                sum_angle_top = sum_angle_top + top_angle
                dist_yel = 0
            except ValueError:
                print("Error calculating top angle!\n")
                print(f"The yel distance is {dist_yel}")
        # Calculate the bottom angle using law of cosines
        if dist_or != 0:
            try:
                bot_angle = math.degrees(math.acos((dist_or**2 - perceived_bot_dist1**2 - perceived_bot_dist2**2)/(-2*perceived_bot_dist1*perceived_bot_dist2)))
                #bot_angle = math.degrees(math.acos((50**2 - perceived_bot_dist1**2 - perceived_bot_dist2**2)/(-2*perceived_bot_dist1*perceived_bot_dist2)))
                # Display bottom angle onto the frame
                #cv2.putText(frame, f"Bottom Angle: {bot_angle:.4f}°", (50,200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)    
                #print("Bottom angle is ", bot_angle)
                # Reset bottom dists
                perceived_bot_dist1 = 0
                perceived_bot_dist2 = 0
                dist_or = 0
                sum_angle_bot = sum_angle_bot + bot_angle
                total_angle = total_angle + 1
            except ValueError:
                print("Error calculating bottom angle!\n")
                print(f"The or distance is {dist_or}")
    timestamp = time.time() - start_time
    # Add data to csv
    data[0].append(top_angle)
    data[1].append(bot_angle)
    data[2].append(" ")
    data[3].append(timestamp)
def find_object_centers(cx, cy, cw, ch, joint):
    global centers1
    global centers2
    global prev_x1, prev_y1
    global prev_x2, prev_y2
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
            if((not (prev_x1 - 2 <= center_x <= prev_x1 + 2) and not (prev_y1 - 2 <= center_y <= prev_y1 + 2))):
                centers1.append((center_x, center_y))
        elif len(centers1) >= 2:
            centers1 = []
    # Find center for bottom objects
    else:
        if centers2 == []:
            centers2.append((center_x, center_y))
            prev_x2 = center_x
            prev_y2 = center_y
        elif len(centers2) == 1:
            # Sort so it doesn't sample the same rectangle twice
            if((not (prev_x2 - 2 <= center_x <= prev_x2 + 2) and not (prev_y2 - 2 <= center_y <= prev_y2 + 2))):
                centers2.append((center_x, center_y))
        elif len(centers2) >= 2:
            centers2 = []

def draw_centers_and_measure(centers, joint):
    global centers1, centers2
    distance_pixels = 0

    if len(centers) >= 2:
        # Calculate and draw the line between centers
        #cv2.line(frame, centers[0], centers[1], (0, 255, 0), 2)
        
        # Calculate the distance between the centers
        distance_pixels = np.linalg.norm(np.array(centers[0]) - np.array(centers[1]))
        distance_mm = distance_pixels * (KNOWN_WIDTH/perceived_width)
        if joint == 1:
            #print(f"Centers1 is {centers1}")
            centers1 = []
        else:
            #print(f"Centers2 is {centers2}")
            centers2 = []
    return distance_pixels
def detect_color(combo, contours):
    global sem
    global dist_or
    global dist_yel
    sem.acquire()
    # or through and find the distances between the centers of the objects (yellow and pink), (green and orange)
    
    for contour in contours:
        #print(contour)
        area = cv2.contourArea(contour)
        if ((area > min_area) and (area < max_area)):
            # Object is larger than minimum area, so proceed with distance calculation
            # Assuming you have the perceived width in pixels (e.g., from bounding box width)
            x, y, w, h = cv2.boundingRect(contour)
            perceived_width = w  # or use h for height, depending on known dimension
            
            # Draw the bounding box for visualization
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if combo == 'or':
                # Find the centers of objects
                find_object_centers(x, y, w, h, 2)
                # Measure the distance
                dist_or = draw_centers_and_measure(centers2, 2)
                #print(f"Centers2 is {centers2} and distance is {dist_or}")
                #print(prev_x2)
                #print(prev_y2)
                #print(f"{combo} countour detected")
                
            else:
                # Find the centers of objects
                find_object_centers(x, y, w, h, 1)
                # Measure the distance
                dist_yel = draw_centers_and_measure(centers1, 1)
                #print(f"Centers1 is {centers1} and distance are {dist_yel}")
                #print(prev_x1)
                #print(prev_y1)
                #print(f"{combo} countour detected")
            if dist_yel or dist_or != 0:
                # Calculate and display the angles of each joint on the frame
                find_angles_and_display(frame, dist_yel, dist_or)
    sem.release()

def process_frame(frame):

    # Convert the frame to the HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Create a mask for the specified color range (yellow and orange)
    yellow_mask = cv2.inRange(hsv, color_lower_yellow, color_upper_yellow)
    orange_mask = cv2.inRange(hsv, color_lower_orange, color_upper_orange)


    # Find contours in the image
    contour_yel, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_or, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_dict = {
        'yel': contour_yel,
        'or': contour_or
    }
    threads = []
    for combo, contour_value in contours_dict.items():
        #print(contour_value)
        thread = threading.Thread(target=detect_color, args=(combo, contour_value))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()



if __name__ == "__main__":
    global start_time 
    start_time = time.time()
    while True:
        # Capture a single frame
        ret, frame = cap.read()
        if not ret:
            break
        
        process_frame(frame)        # Process frame and create threads
        
        # Display the resulting frame
        cv2.imshow('Frame', frame)
        
        # Exit the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            #avg_distance = distance_sum/distance_num
            #print(f"Average Distance is {avg_distance:.2f} from {distance_num} data points")
            # calculate average angle of top and bottom
            avg_angle_top = sum_angle_top/total_angle
            avg_angle_bot = sum_angle_bot/total_angle
            print(f"Top Angle is {avg_angle_top}")
            print(f"Bottom Angle is {avg_angle_bot}")
            data[0].append(" ")
            data[1].append(" ")
            data[2].append(" ")
            data[3].append(" ")
            data[0].append(avg_angle_top)
            data[1].append(avg_angle_bot)
            data[2].append(" ")
            data[3].append(" ")
            # Open file and create writer object
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(list(zip(*data)))
            break

    # Release the capture and close all windows
    cap.release()
    cv2.destroyAllWindows()