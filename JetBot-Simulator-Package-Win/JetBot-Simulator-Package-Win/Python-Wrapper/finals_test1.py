from jetbotSim import Robot, Camera
import numpy as np
import cv2
from time import perf_counter

prev_time = perf_counter()
WIDTH = 1280
HEIGHT = 720
HALF_WIDTH = 640
STOP_FLAG = 0
LAST_ROW_BIAS = -250 # +250 to 250 should be safely within boundry
# KERNEL = np.ones((5,5),np.uint8)
def execute(change):
    global prev_time,STOP_FLAG
    curr_time = perf_counter()
    time_step = curr_time-prev_time
    curr_frame = change['new']
    hsv_frame = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2HSV)
    red_frame = cv2.inRange(hsv_frame, (160, 50, 20), (179, 255, 255))
    red_frame = red_frame + cv2.inRange(hsv_frame, (0,50,20), (10,255,255))
    black_frame = cv2.inRange(hsv_frame,(0,0,0),(180,255,150))
    # print(red_frame.shape)
    last_row = red_frame[LAST_ROW_BIAS,:]
    lateral_bias = -250
    left = -1
    best_len,mid = 0,-1
    for x,dot in enumerate(last_row):
        if dot > 0:
            if left == -1:
                left = x
            if x-left+1 > best_len:
                best_len = x-left+1
                mid = (x+left)//2
        else:
            left = -1
    target = HALF_WIDTH+lateral_bias
    mid_diff = abs(mid-target)/WIDTH
    if best_len == 0:
        robot.stop()
        STOP_FLAG = 5
    elif STOP_FLAG > 0:
        STOP_FLAG -= 1
    else:
        robot.forward(0.2)
        if mid > target+20:
            robot.add_motor(0.05*mid_diff,-0.05*mid_diff)
        elif mid < target-20:
            robot.add_motor(-0.05*mid_diff,0.05*mid_diff)

    red_frame_out = cv2.cvtColor(red_frame+black_frame,cv2.COLOR_GRAY2BGR)
    out_str = str(mid)
    if mid > target:
        out_str = "   " + out_str + ">>>"
    elif mid < target:
        out_str = "<<<" + out_str + "   "
    else:
        out_str = "   " + out_str + "   "
    cv2.rectangle(red_frame_out,(mid-10,HEIGHT+LAST_ROW_BIAS-20),(mid+10,HEIGHT+LAST_ROW_BIAS),(0,0,255),3)
    cv2.rectangle(red_frame_out,(target-10,HEIGHT+LAST_ROW_BIAS-20),(target+10,HEIGHT+LAST_ROW_BIAS),(0,255,0),3)
    cv2.putText(red_frame_out,out_str,(mid-75,HEIGHT+LAST_ROW_BIAS-40),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),1,cv2.LINE_AA)
    cv2.imshow("camera", red_frame_out)

    prev_time = curr_time
robot = Robot()
camera = Camera()
camera.observe(execute)