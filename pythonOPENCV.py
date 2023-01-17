import requests
import cv2 as cv
import time
import numpy as np
import math

# st = time.time()
# image = cv.imread("D:\my stuff\TYProject\DIP_P1\capture5.jpg")
# image = image[0:300, 50:700];
# image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
# imageC = cv.bitwise_not(image);
# image = cv.filter2D(image, -1, np.ones([5, 5]) / 25)
# imageEnh = cv.adaptiveThreshold(image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
# canny_output = cv.Canny(imageEnh, 80, 150, )
# cannyBlb = cv.dilate(canny_output, np.ones([5, 5], np.uint8));
# # cv.imshow('canny', canny_output);
# # cv.imshow('canny2', cannyBlb)
# cdstP = cv.cvtColor(cannyBlb, cv.COLOR_GRAY2BGR)
# linesP = cv.HoughLinesP(cannyBlb, 1, np.pi / 180, 50, None, 50, 10)
# pos1 = 0
# pos2 = 0
# if linesP is not None:
#     for i in range(0, len(linesP)):
#         l = linesP[i][0]
#         pos1 += l[1]
#         pos2 += l[3]
# pos1 = math.floor(pos1/ (len(linesP) + 1))
# pos2 = math.floor(pos2 / (len(linesP) + 1))
# avp=pos1+pos2
# avp/=2
# # cv.line(cdstP, (0, pos1), (650, pos2), (255, 150, 120), 1, cv.LINE_AA)
# threshP=40
# threshC=100
# probF=0;
# faultL=[]
# for x in range(0,300):
#     for y in range(0,650):
#         if canny_output[x][y]==255 and abs(x-avp)>threshP:
#             cdstP[x][y]=[0,0,255]
#             faultL.append([x,y]);
#             probF+=1
# # cv.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdstP)
# print(time.time() - st)
# if(probF>threshC):
#     print('!! mechanical failure detected !!')
#     print('fault detected at pixel locations:')
#     print(faultL)

url ='http://192.168.0.104/capture?_cb='
requests.get('http://192.168.0.104/control?var=framesize&val=8')
while(True):
    st = time.time()
    img = requests.get(url + str(time.time()), stream=True).raw
    image = np.asarray(bytearray(img.read()), dtype='uint8')
    image = cv.imdecode(image, cv.IMREAD_COLOR)
    image=image.astype(np.uint8)
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image = image[0:300, :];
    imageC = cv.bitwise_not(image);
    image = cv.filter2D(image, -1, np.ones([5, 5]) / 25)
    imageEnh = cv.adaptiveThreshold(image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
    canny_output = cv.Canny(imageEnh, 80, 150, )
    cannyBlb = cv.dilate(canny_output, np.ones([5, 5], np.uint8));
    cdstP = cv.cvtColor(cannyBlb, cv.COLOR_GRAY2BGR)
    linesP = cv.HoughLinesP(cannyBlb, 1, np.pi / 180, 50, None, 50, 10)
    pos1 = 0
    pos2 = 0
    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            pos1 += l[1]
            pos2 += l[3]
    pos1 = math.floor(pos1 / (len(linesP) + 1))
    pos2 = math.floor(pos2 / (len(linesP) + 1))
    avp = pos1 + pos2
    avp /= 2
    cv.line(cdstP, (0, pos1), (650, pos2), (255, 150, 120), 1, cv.LINE_AA)
    threshP = 40
    threshC = 100
    probF = 0;
    faultL = []
    for x in range(0, 300):
        for y in range(0, 640):
            if canny_output[x][y] == 255 and abs(x - avp) > threshP:
                cdstP[x][y] = [0, 0, 255]
                faultL.append([x, y]);
                probF += 1
    cv.imshow('img', cdstP)
    # if (probF > threshC):
    #     print('!! mechanical failure detected !!')
    #     print('fault detected at pixel locations:')
    #     print(faultL)
    en = time.time()
    print((en - st) * 1000)
cv.waitKey()
