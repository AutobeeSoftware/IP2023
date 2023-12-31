import cv2
import numpy as np
import sys
sys.path.append(r"../IP2023")

from utils2 import gstreamer_pipeline, camCombine

import threading
import numpy as np

from CSI_Camera import CSI_Camera


#frameL = cv2.VideoCapture(gstreamer_pipeline(0),cv2.CAP_GSTREAMER)
#frameR = cv2.VideoCapture(gstreamer_pipeline(1),cv2.CAP_GSTREAMER)

left_camera = CSI_Camera()
left_camera.open(gstreamer_pipeline(0))
left_camera.start()

right_camera = CSI_Camera()
right_camera.open(gstreamer_pipeline(1))
right_camera.start()


_, frameL = left_camera.read()
_, frameR = right_camera.read()

width = frameL.shape[1]
heigth = frameL.shape[0]
print((width , heigth))





def empty(img):
    pass

cv2.namedWindow("TrackBar")  
cv2.resizeWindow("TrackBar", heigth+30, width*2, )
cv2.createTrackbar("overlap", "TrackBar", 0, width*2, empty)

# click s to save click q to quit


while True:  
    

    overlap = cv2.getTrackbarPos("overlap", "TrackBar")
    _, frameL = left_camera.read()
    _, frameR = right_camera.read()

    combined = camCombine(frameL, frameR,overlap)

    cv2.putText(combined, "left cam", (int(0), 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(combined, "right cam" , (int(width-10), 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 1, cv2.LINE_AA)
    

    cv2.imshow("TrackBar", combined)  
    cv2.getTrackbarPos("TrackBar", "Frame")
    k = cv2.waitKey(30)  
    
    if k == ord('q'):  
        break
    
    if k == ord('s'):  
        print("overlap: " + str(overlap))


frameL.stop()
frameR.stop()

frameL.release()
frameR.release()

cv2.destroyAllWindows()