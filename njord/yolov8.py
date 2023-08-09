
import cv2
import numpy as np
from ultralytics import YOLO
import sys
import os

sys.path.append(os.path.abspath('../IP_general'))

import utils2

# Load a pretrained YOLOv8n model
model = YOLO('/content/drive/MyDrive/njord/yolo/yolov8n-v1-320-e100/train/weights/best.pt')
names = model.names
# Define path to video file
source = '/content/drive/MyDrive/njord/data/prop/16.jpeg'
img = cv2.imread(source)



# Run inference on the source
results = model(source, device=0,augment=True)  # generator of Results objects
r = results[0]

index = 0
for i in r.boxes.cls:
    cls = names[int(i)]
    bbox = r.boxes.xyxy[index]
    index += 1
    fov = utils2.bbox2fov(img,bbox,73)
    print("------")
    #print(check_cardinal(img,bbox,cls))
