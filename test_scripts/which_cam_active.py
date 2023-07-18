import sys
sys.path.append("../IP2023")


from CSI_Camera import CSI_Camera
import cv2

cam1 = CSI_Camera() # primer camera
cam2 = CSI_Camera()# seconder camera
id_ = {cam1 : "0001", cam2: "0002"}


cam1.open(CSI_Camera.gstreamer_pipeline(0))
cam2.open(CSI_Camera.gstreamer_pipeline(1))

while True:

    ret1, frame1 = cam1.read()
    ret2, frame2 = cam2.read()

    if ret1 is False and ret2 is False: # if both cam are not active
        print(f"{id_[cam1]}\n{id_[cam2]}")
        break
    elif ret1 is not True: # if only cam1 is not active
        print(id_[cam1])
        break
    elif ret2 is not True: # if only cam2 is not active
        print(id_[cam2])
        break

    cv2.imshow("cam1", frame1)
    cv2.imshow("cam2", frame2)
    cv2.waitKey(30)

cam1.stop()
cam2.stop()

cam1.release()
cam2.release()
cv2.destroyAllWindows()