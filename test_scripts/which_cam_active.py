import sys
sys.path.append("../IP2023")


from CSI_Camera import CSI_Camera
import cv2

cam1 = CSI_Camera() # primer camera
cam1_is_open = False

cam2 = CSI_Camera()# seconder camera
cam2_is_open = False


try:
    cam1.open(CSI_Camera.gstreamer_pipeline(0))
    cam1_is_open = True

except:
    print("Cam1 is failed to open")
    pass

try:
    cam2.open(CSI_Camera.gstreamer_pipeline(1))
    cam2_is_open = True

except:
    print("Cam2 is failed to open")
    pass



while cam1_is_open and cam2_is_open :


    if cam1_is_open is False and cam2_is_open is False: 
        print("No camera to read")
        break
    elif cam1_is_open is True and cam2_is_open is False: 
        ret1, frame1 = cam1.read()
        if ret1 == False:
            print("cam1 is opened but couldnt read")
            break
        else:
            cv2.imshow("cam1", frame1)
            cv2.waitKey(3)

    elif cam1_is_open is False and cam2_is_open is True: 
        ret2, frame2 = cam2.read()
        if ret2 == False:
            print("cam2 is opened but couldnt read")
            break
        else:
            cv2.imshow("cam2", frame2)
            cv2.waitKey(3)

    else:
        ret1, frame1 = cam1.read()
        ret2, frame2 = cam2.read()

        if ret1 == False and ret2 == False:
            print("cam1 and cam2 are opened but couldnt read")
            break

        elif ret1 == True and ret2 == False:
            print("cam2 is opened but couldnt read")
            print("cam1 is working")
            cv2.imshow("cam1", frame1)
            cv2.waitKey(3)

        elif ret1 == False and ret2 == True:
            print("cam1 is opened but couldnt read")
            print("cam2 is working")
            cv2.imshow("cam2", frame2)
            cv2.waitKey(3)

        else:
            cv2.imshow("cam1", frame1)
            cv2.imshow("cam2", frame2)

            cv2.waitKey(30)




cam1.stop()
cam2.stop()

cam1.release()
cam2.release()
cv2.destroyAllWindows()