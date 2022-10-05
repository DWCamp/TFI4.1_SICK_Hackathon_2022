"""
Code for processing receiving camera images and using computer
vision to detect gesture commands

Author: Serhii Voronov
Version: 2022-10-05
"""

import cv2
import mediapipe as mp
import time
import threading
import shutil
import sys
import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pathlib import Path
import glob
import os
import math


X = 0
Y = 1

LEFT_HAND = 15
RIGHT_HAND = 16
LEFT_SHOLDER = 11
RIGHT_SHOLDER= 12

LEFT_EYE = 3
RIGHT_EYE = 6

LEFT_HIP = 23
RIGHT_HIP= 24

FTP_PORT = 21
FTP_USER = "admin"
FTP_PASSWORD = "admin"
FTP_DIRECTORY = "/Users/voronov/Desktop/SICK/camera"

CAMERA_MAC = os.name == "Darwin"


def server_ftp():
    print("START SERVER")
    try:
        shutil.rmtree("/Users/voronov/Desktop/SICK/camera/nova", ignore_errors=False, onerror=None)
    except:
        pass
    time.sleep(2)
    try:
        os.mkdir("/Users/voronov/Desktop/SICK/camera/nova")
    except:
        pass
    time.sleep(3)
    authorizer = DummyAuthorizer()
    authorizer.add_user(FTP_USER, FTP_PASSWORD, FTP_DIRECTORY, perm='elradfmw')
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "pyftpdlib based ftpd ready."
    address = ('192.168.0.2', FTP_PORT)
    server = FTPServer(address, handler)
    server.max_cons = 256
    server.max_cons_per_ip = 5
    server.serve_forever()
    print("SERVER STARTED")


def put_texts_on_stream(img, id, cx, cy):
    if id == LEFT_SHOLDER:
        cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)
        cv2.putText(img, str("left sholder"), (cx, cy - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        #cv2.putText(img, str("cx:" + str(cx) + "cy" + str(cy)), (cx, cy - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),1)
    elif id == RIGHT_SHOLDER:
        cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)
        cv2.putText(img, str("right sholder"), (cx, cy - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        #cv2.putText(img, str("cx:"+str(cx)+"cy"+str(cy)), (cx, cy - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
    else:
        cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)
    # left  hand
    if id == LEFT_HAND:
        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str("left hand"), (cx, cy - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    # right hand
    if id == RIGHT_HAND:
        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str("right hand"), (cx, cy - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


def person_look_forward(id_positions, img):
    if LEFT_SHOLDER in id_positions.keys() and RIGHT_SHOLDER in id_positions.keys():
        if id_positions[LEFT_SHOLDER][X] > id_positions[RIGHT_SHOLDER][X]:
            #cv2.putText(img, str("LOOK FORWARD"), (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
            return True
    return False


def dot(v_a, v_b):
    return v_a[0] * v_b[0] + v_a[1] * v_b[1]


def ang(line_a, line_b):
    vA = [(line_a[0][0] - line_a[1][0]), (line_a[0][1] - line_a[1][1])]
    vB = [(line_b[0][0] - line_b[1][0]), (line_b[0][1] - line_b[1][1])]
    dot_prod = dot(vA, vB)

    magA = dot(vA, vA) ** 0.5
    magB = dot(vB, vB) ** 0.5

    cos_ = dot_prod / magA / magB

    angle = math.acos(dot_prod / magB / magA)

    ang_deg = math.degrees(angle) % 360
    ang_deg = int(ang_deg)
    if ang_deg - 180 >= 0:
        ang_deg = 360 - ang_deg
        if ang_deg < 90:
            ang_deg = - (90 - ang_deg)
        else:
            ang_deg = ang_deg%90
        return ang_deg
    else:
        if ang_deg < 90:
            ang_deg = - (90 - ang_deg)
        else:
            ang_deg = ang_deg%90
        return ang_deg


def file_detection():
    if not CAMERA_MAC:
        try:
            shutil.rmtree("/Users/voronov/Desktop/SICK/camera/nova", ignore_errors=False, onerror=None)
        except:
            pass
        time.sleep(2)
        try:
            os.mkdir("/Users/voronov/Desktop/SICK/camera/nova")
        except:
            pass
    else:
        cap = cv2.VideoCapture(0)
    time.sleep(3)

    mpPose = mp.solutions.pose
    pose = mpPose.Pose()
    mpDraw = mp.solutions.drawing_utils

    pTime = 0
    fps = 0
    while True:
            if not CAMERA_MAC:
                try:
                    list_of_files = glob.glob(
                        '/Users/voronov/Desktop/SICK/camera/nova/*')
                    latest_file = max(list_of_files, key=os.path.getctime)
                    #print(latest_file)
                except:
                    #print("EMPTY FOLDER")
                    continue
            if CAMERA_MAC:
                success, img = cap.read(0)
                img_normal = img
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                try:
                    img = cv2.imread(latest_file)
                    img_normal = img
                    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = img_gray
                except:
                    print("can not read the picture ")
                    continue
            results = pose.process(img_normal)

            #print(results.pose_landmarks)
            if results.pose_landmarks:

                cv2.putText(img, str("Operator is in the view "), (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                if not CAMERA_MAC:
                    mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
                id_positions = {}
                for id, lm in enumerate(results.pose_landmarks.landmark):
                    if CAMERA_MAC:
                        h, w = img.shape
                    else:
                        h, w, c = img.shape
                    #print(id, lm)
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    put_texts_on_stream(img,id,cx,cy)
                    id_positions[id] = (cx,cy)
                left_hand_up = False
                right_hand_up = False
                backvard = False
                if person_look_forward(id_positions,img):
                    pos = id_positions.keys()
                    if LEFT_EYE  in pos and LEFT_HAND  in pos and LEFT_SHOLDER  in pos and \
                       RIGHT_EYE in pos and RIGHT_HAND in pos and RIGHT_SHOLDER in pos and \
                         id_positions[LEFT_SHOLDER][Y]  > id_positions[LEFT_HAND][Y]  > id_positions[LEFT_EYE][Y] and \
                         id_positions[RIGHT_SHOLDER][Y] > id_positions[RIGHT_HAND][Y] > id_positions[RIGHT_EYE][Y]:
                                backvard = True

                    if LEFT_SHOLDER in id_positions.keys() and LEFT_HAND in id_positions.keys():
                        if id_positions[LEFT_HAND][Y] < id_positions[LEFT_SHOLDER][Y]:
                            left_hand_up = True
                            cv2.putText(img, str("HAND UP"), (id_positions[LEFT_HAND][X]+10, id_positions[LEFT_HAND][Y] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    if RIGHT_SHOLDER in id_positions.keys() and RIGHT_HAND in id_positions.keys():
                        if id_positions[RIGHT_HAND][Y] < id_positions[RIGHT_SHOLDER][Y]:
                            right_hand_up = True
                            cv2.putText(img, str("HAND UP"), (id_positions[RIGHT_HAND][X]+10, id_positions[RIGHT_HAND][Y] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    if backvard:
                        cv2.putText(img, str("Move backward"), (0, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    elif left_hand_up and right_hand_up:
                        cv2.putText(img, str("Move toward"), (0,70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    elif left_hand_up:
                        cv2.putText(img, str("Move to the left"), (0, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    elif right_hand_up:
                        cv2.putText(img, str("Move to the right"), (0, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    else:
                        cv2.putText(img, str("STOP"), (0, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                else:
                    cv2.putText(img, str("Follow position"), (0, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    if RIGHT_HIP in id_positions.keys() and LEFT_HIP in id_positions.keys():
                        center = (
                        int(id_positions[LEFT_HIP][X] + (id_positions[RIGHT_HIP][X] - id_positions[LEFT_HIP][X]) / 2),
                        int(id_positions[LEFT_HIP][Y] + (id_positions[RIGHT_HIP][Y] - id_positions[LEFT_HIP][Y]) / 2))
                        cv2.circle(img, center, 10, (0, 0, 255), cv2.FILLED)
                        #cv2.putText(img, str("CENTER"), center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

                        cv2.line(img, (int(img.shape[0]/2), img.shape[1]), center, (0, 255, 0), 3)
                        ang_act = ang([center,[int(img.shape[0]/2), img.shape[1]]], [[int(img.shape[0]/2), img.shape[1]],[int(img.shape[0]), img.shape[1]]])
                        cv2.putText(img, str(ang_act), (center[0], center[1]-40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                    elif RIGHT_SHOLDER in id_positions.keys() and LEFT_SHOLDER in id_positions.keys():
                        center = (
                        int(id_positions[LEFT_SHOLDER][X] + (id_positions[RIGHT_SHOLDER][X] - id_positions[LEFT_SHOLDER][X]) / 2),
                        int(id_positions[LEFT_SHOLDER][Y] + (id_positions[RIGHT_SHOLDER][Y] - id_positions[LEFT_SHOLDER][Y]) / 2))
                        cv2.circle(img, center, 10, (0, 0, 255), cv2.FILLED)
                        #cv2.putText(img, str("CENTER"), center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0), 3)

                        cv2.line(img, (int(img.shape[0] / 2), img.shape[1]), center, (0, 255, 0), 5)
                cTime = time.time()
                #fps = 1/(cTime-pTime)
                pTime = cTime
            else:
                cv2.putText(img, str("STOP"), (0, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            #cv2.putText(img, str(int(fps)), (50,50), cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0), 3)
            scale_percent = 300  # percent of original size
            width = int(img.shape[1] * scale_percent / 100)
            height = int(img.shape[0] * scale_percent / 100)
            dim = (width, height)

            # resize image
            resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

            cv2.imshow("Image", resized)
            cv2.waitKey(1)
            if not CAMERA_MAC:
                os.remove(latest_file)
            #time.sleep(1
            #cv2.waitKey(0)


if not CAMERA_MAC:
    thread1 = threading.Thread(target=server_ftp, args=())
    thread1.start()
file_detection()
if not CAMERA_MAC:
    thread1.join()




