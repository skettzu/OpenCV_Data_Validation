import cv2
import time

def list_cameras(max_cameras=3000):
    available_cameras = []
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        print(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
            print(f"Camera {i} is available")
    return available_cameras

cameras = list_cameras()
print(f"Available cameras: {cameras}")
time.sleep(10)