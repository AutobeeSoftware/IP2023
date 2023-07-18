import CSI_camera


cam1 = CSI_Camera() # primer camera
cam2 = CSI_Camera()# seconder camera
id_ = {cam1 : "0001", cam2: "0002"}

flag = 0

try:
    cam1.open()
    flag +=1
except:
    except Exception as e: 
        print(e)


try:
    cam2.open()
    flag+=1
except:
    except Exception as e: 
        print(e)


while flag > 0:

    ret1, frame1 = cam1.read()
    ret2, frame2 = cam2.read()

    cv2.imshow("cam1", frame1)
    cv2.imshow("cam2", frame2)
    cv2.waitKey(30)

cv2.destroyAllWindows()