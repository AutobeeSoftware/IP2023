
import cv2
import numpy as np
from ultralytics import YOLO
import sys
import os
import time

sys.path.append(os.path.abspath('../IP_general'))

import utils2

### fps icin ###
prev_image_time = 0
new_image_time = 0
a = 0
################


##################
# Prepare
w, h = 1280, 720 #### ??
fx, fy = 1027.3, 1026.9 #### ??

# Go
fov_x = np.rad2deg(2 * np.arctan2(w, 2 * fx))
fov_y = np.rad2deg(2 * np.arctan2(h, 2 * fy))
print(fov_x)
print(fov_y)
##############


model_path = ""
#img_soure = ""

camera = utils2.CSI_Camera()
camera.open(utils2.gstreamer_pipeline(0))
camera.start()

while True:
    _ , frame = camera.read()

    if _ == False:
        break

    objects = utils2.detect(model_path,frame,fov_x)
    print(objects)


    ### fps icin ##
    new_image_time = time.time()
    fps = 1 / (new_image_time - prev_image_time)
    prev_image_time = new_image_time
    print(f"*******  FPS : {fps}  ********")
    ##########


camera.stop()
camera.release()

    
