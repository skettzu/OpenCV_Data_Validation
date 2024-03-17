OpenCV Computer Vision Data Validation for Tatum T1

Main Distance Measuring Script: open_cv_test.py

Notes:

Before executing tests, please ensure the script is operating with an appropriate margin error. To test for accuracy follow the steps below:

1. Stick two stickers to a piece of paper or any object of your choice
2. Measure the distance between the centers of the stickers and note it
3. Run the script and start moving the piece of paper around on the x/y axis, keep the piece of paper perpendicular to the camera
4. Once you have around ~1 minute worth of samples press 'q' to stop the script
5. In the console it will print the average distance calculated, ensure that this number is within the expected margin of error

Further Improvements:
- Will need to adjust minimum area detected according to the area of the stickers used for the testing unit
- Ability to store data points in a resulting excel sheet for analysis
    - Automated calculation of angles between joints
- Utilization of multi-colored stickers if three points of interest are needed