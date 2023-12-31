import cv2
import numpy as np
from scipy import ndimage
import math
import time
from ultralytics import YOLO


def masking(hsv, lower_hsv, upper_hsv, opening_kernel = 2, medianF_tresh = 2, horizon_tresh = 0):
    width = hsv.shape[1]

    # creating mask
    #hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    
    if horizon_tresh > 0 :
        cv2.rectangle(mask, (0,0), (width,horizon_tresh), (0, 0, 0), -1)

    mask = cv2.bitwise_and(mask, mask, mask=mask)

    if opening_kernel > 0:
        # applying opening operation
        kernel = np.ones((opening_kernel, opening_kernel), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    if medianF_tresh > 0:
    # removing parasites
        mask = ndimage.median_filter(mask, size=medianF_tresh)

    return mask

def bounding_box(mask,tresh,tag):

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    params = []
    if len(contours) > 0:
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        for c in sorted_contours[:4]:
            obj_area = cv2.contourArea(c)
            
            if obj_area > tresh:
                x, y, w, h = cv2.boundingRect(c)
                params.append([(x+int(w/2), y+int(h/2)),obj_area,tag])

            else:
                print("this object not bigger than treshold")
                
       
        print("next frame")
        

    if len(params) > 0:
        return params
    else:
        return None 


def intersect(mask1,mask2,mask3):

    intersect0 = cv2.bitwise_and(mask1,mask2)
    interset_3 = cv2.bitwise_and(intersect0,mask3)
    return interset_3

def is_center(params,width,tresh):

    if params != None:
        (cx,cy),area,tag = params
        if cx<int(width/2-tresh):
            print("on the left")
            cx_string = "left"
        elif cx>int(width/2+tresh):
            print("on the right")
            cx_string = "right"
        else:
            print("on the middle")
            cx_string = "middle"
        params.append(cx_string)
        print(params)

        return params

    else:
        return None


def closest(params):
    if params != None:
        cache = 0
        ind = None
        for index,object in enumerate(params):
            (cx,cy), area, tag = object
            if cache < cy:
                cache = cy
                ind = index
            else:
                continue
        if ind != None:
            return params[ind]
    else:
        return None




def gstreamer_pipeline(
    sensor_id=0,
    capture_width=480,
    capture_height=360,
    display_width=480,
    display_height=360,
    framerate=30,
    flip_method=0,
):

    """
    >>cv2.VideoCapture(gstreamer_pipeline()) 
    """
    return (
        "nvarguscamerasrc sensor-id=%d !"
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

def between_buoys(objs1, objs2): 
    # objs1 should on the rigth side
    ccx = 0
    ccy = 0
    isForward = None
    distence=0

    center_of_obj1 = closest(objs1)
    center_of_obj2 = closest(objs2)

    if center_of_obj1 != None  and  center_of_obj2 != None:
        (cx1,cy1), area1, tag1 = center_of_obj1
        (cx2,cy2), area2, tag2 = center_of_obj2

        ccx = int((cx1 + cx2)/2)
        ccy = int((cy1 + cy2)/2)
        distence = int(math.sqrt((cx1-cx2)**2 + (cy1 - cy2)**2))

        if cx1 > cx2:
            isForward = True
        else:
            isForward = False
    
    elif center_of_obj1 == None  and  center_of_obj2 != None:
        (cx2,cy2), area2, tag2 = center_of_obj2
        ccx = cx2
        ccy = cy2
        print(f"no object: {tag2}")

    elif center_of_obj1 != None  and  center_of_obj2 == None:
        (cx1,cy1), area1, tag1 = center_of_obj1
        ccx = cx1
        ccy = cy1
        print(f"no object: {tag1}")
    else:
        
        print("no objects")

    return [(ccx,ccy),isForward,distence]
   


def camCombine(frameL,frameR,overlap):
    # İki kameradan alınan kareleri aynı boyuta getiriyoruz
   
    if frameL.shape[0] == frameR.shape[0] and frameL.shape[1] == frameR.shape[1]:
        h = frameL.shape[0]
        w = frameR.shape[1]
        frameL = frameL[:h, : w - overlap] 
        frameR = frameR[:h, overlap :]

        # İki kareyi yatay olarak birleştiriyoruz
        combined_frame = np.hstack((frameL, frameR))


        return combined_frame

    else:
        return None

def camera2lidar(width, fov,detections):
    if detections != None:
        output = [0 for i in range(270)] 
        shift = int((270-fov)/2)
        ratio = fov/width 

        for i in detections:
            (cx, cy), area, id = i
            
            radius =  int(math.pow(area/3,0.5))
            start = int((cx - radius) * ratio)
            end = int((cx + radius) * ratio)
            print("start ,end , radius")
            print(start,end,radius)
            
            for j in range(shift+start,shift+end+1):
                output[j] = id
                
        return output
    else:
        return None


def lidar2cam(img, fov,lidar,treshold):
    if lidar is None:
        return None 

    shift = int((len(lidar)-fov)/2)
    lidar = np.array(lidar)
    camera_fov = lidar[shift:len(lidar)-shift]

    output_image = np.copy(img)
    mask = np.array(camera_fov<treshold)
    
    width = img.shape[1]
    for col in range(width):
        new_idx = int(fov * col / width)
        #print(mask.shape, new_idx)
        if not mask[new_idx]:
            output_image[:, col] = [0, 0, 0]

    return output_image


def mask_with_lidar(img, cam_fov,circles):
    if circles is None:
        return None
    
    frame_fov = np.zeros(cam_fov)
    width = img.shape[1]
    output_image = np.copy(img)


    for circle in circles:
        x, y = circle
        d = math.pow(x**2 + y**2 ,1/2)
        print(d)
        r = 0.15

        center_angle = math.degrees(math.atan2(y,x))
        radius_angle = math.degrees(abs(math.atan2(r,d)))
        
        fov_start = min(center_angle-radius_angle, center_angle+radius_angle)
        fov_end = max(center_angle-radius_angle, center_angle+radius_angle)
        print(fov_start,fov_end)



        if fov_end < -cam_fov/2 or fov_start > cam_fov/2:
            continue
        else:
            frame_fov[int(fov_start+cam_fov/2):int(fov_end+cam_fov/2)] = 1
            
            print("yolo")
    

    for col in range(width):
        new_idx = int(cam_fov * col / width)
        #print(mask.shape, new_idx)
        print(frame_fov[new_idx])
        if not frame_fov[new_idx]:
            output_image[:, col] = [0, 0, 0]    
        
            
    return output_image
   


def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
     
        return roll_x, pitch_y, yaw_z # in radians

def mask_with_imu(img,cam_fov,data):
    roll,pitch,yaw = data
    yaw = math.degrees(yaw)
    frame_fov = np.zeros(cam_fov)
    heigth = img.shape[0]
    output_image = np.copy(img)

    if yaw < 0:
        print(int(cam_fov-yaw))
        frame_fov[0:int(cam_fov+yaw)] = 1
    elif yaw > 0 :
        frame_fov[int(yaw):cam_fov] = 1

    print("yolo")


    for row in range(heigth):
        new_idx = int(cam_fov * row / heigth)
        #print(mask.shape, new_idx)
        print(frame_fov[new_idx])
        if not frame_fov[new_idx]:
            output_image[row, :] = [0, 0, 0]    
        
            
    return output_image


def bbox2fov(img,bbox,fov):
    w = img.shape[1]
    x1,y1,x2,y2 = bbox
    start_fov = x1*fov/w
    end_fov = x2*fov/w

    start_fov = start_fov - (fov/2)
    end_fov = end_fov - (fov/2)

    return [start_fov,end_fov]



def detect(model_path,img,fov_x):
    # Load a pretrained YOLOv8n model
    model = YOLO(model_path)
    names = model.names
    # Define path to video file
    



    # Run inference on the source
    results = model(img, device=0)  # generator of Results objects
    r = results[0]
    tstmp = time.time()
    
    
    out = []
    index = 0
    for i in r.boxes.cls:
        cls = names[int(i)]
        bbox = r.boxes.xyxy[index]
        index += 1
        fov = bbox2fov(img,bbox,fov_x)

        obj = {"time_stamp":tstmp,
               "class":cls,
               "fov_center":(fov[0] + fov[1])/2,
               "fov_start" : fov[0],
               "fov_end" :fov[1]
               }
        out.append(obj)
        print("obj")
        #print(check_cardinal(img,bbox,cls))
    
    return out
