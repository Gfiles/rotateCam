import json
import pyvirtualcam #pip install pyvirtualcam
import json
import sys
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0" #https://github.com/opencv/opencv/issues/17687
import cv2 #pip install opencv-python, https://docs.opencv.org/4.x/d4/d15/group__videoio__flags__base.html#gga023786be1ee68a9105bf2e48c700294da38a8d4494036d9a1cc3227dee9189755

def readConfig():
    settingsFile = os.path.join(cwd, "config.json") 
    if os.path.isfile(settingsFile):
        with open(settingsFile) as json_file:
            data = json.load(json_file)
    else:
        data = {
	        "camNumber" : 0,
            "resolutionIn" : [3840, 2160],
	        "frameRate" : 24,
            "resolutionOut" : [1080, 1920],
	        "rotation" : 90,
            "crop" : 1
            }
        # Serializing json
        json_object = json.dumps(data, indent=4)
 
        # Writing to config.json
        with open(settingsFile, "w") as outfile:
            outfile.write(json_object)
    return data

# Get the current working
# directory (CWD)
try:
    this_file = __file__
except NameError:
    this_file = sys.argv[0]
this_file = os.path.abspath(this_file)
if getattr(sys, 'frozen', False):
    cwd = os.path.dirname(sys.executable)
else:
    cwd = os.path.dirname(this_file)

print("Current working directory:", cwd)

# Read Config File
config = readConfig()
camNumber = config["camNumber"]
resolutionIn = config["resolutionIn"]
frameRate = config["frameRate"]
resolutionOut = config["resolutionOut"]
rotation = config["rotation"]
crop = config["crop"]

cap = cv2.VideoCapture(camNumber, cv2.CAP_MSMF)
#cap = cv2.VideoCapture(camNumber, cv2.CAP_ANY )

if not cap.isOpened():
    raise IOError("Cannot open webcam")

print(cv2.videoio_registry.getCameraBackends())
width = resolutionIn[0]
height = resolutionIn[1]
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cap.set(cv2.CAP_PROP_FPS, frameRate)

if crop:
    difX = int((width - resolutionOut[0])/2)
    #print(difX)
    difY = int((height - resolutionOut[1])/2)
    with pyvirtualcam.Camera(width=resolutionOut[0], height=resolutionOut[1], fps=frameRate, fmt=pyvirtualcam.PixelFormat.BGR) as cam:    
        try:        
            print(f'Using virtual camera: {cam.device}')
            while True:
                ret, frame = cap.read()
                # Crop
                cropped_frame = frame[difY:resolutionOut[1]+difY, difX:resolutionOut[0]+difX]
                #cropped_image = rotated_frame[0:1080, 10:1920]
                cam.send(cropped_frame)
                cam.sleep_until_next_frame()
        except KeyboardInterrupt:
            cap.release()
else:
    if rotation == 90:
        rotationType = cv2.ROTATE_90_CLOCKWISE
    elif rotation == 180:
        rotationType = cv2.ROTATE_180
    elif rotation == 270:
        rotationType = cv2.ROTATE_90_COUNTERCLOCKWISE
    
    with pyvirtualcam.Camera(width=resolutionOut[0], height=resolutionOut[1], fps=frameRate, fmt=pyvirtualcam.PixelFormat.BGR) as cam:    
        try:        
            print(f'Using virtual camera: {cam.device}')
            while True:
                ret, frame = cap.read()
                # resize image
                rotated_frame = cv2.rotate(frame, rotationType)
                cam.send(rotated_frame)
                cam.sleep_until_next_frame()
        except KeyboardInterrupt:
            cap.release()