# coding=utf-8
import csv
import cv2
import sys
import numpy as np
import time
from PIL import Image
import matplotlib.pyplot as plt
from pymouse import PyMouse
from pykeyboard import PyKeyboard
import pyscreenshot as ImageGrab
import pytesseract

# take the longitude and latitude of the four vertex of the solar cell pack, calculate the location of each cell and write the result in the csv


def returncvs(left_upper_long, left_upper_lati, left_lower_long, left_lower_lati, right_upper_long, right_upper_lati, right_lower_long, right_lower_lati):
    x = (right_upper_long-left_upper_long+right_lower_long-left_lower_long)/266
    y = -(right_upper_lati-right_lower_lati+left_upper_lati-left_lower_lati)/6
    myfile = open('result.csv', 'w')
    with myfile:
        writer = csv.writer(myfile)
        writer.writerow(['left_upper_long', 'left_upper_lati', 'left_lower_long', 'left_lower_lati',
                         'right_upper_long', 'right_upper_lati', 'right_lower_long', 'right_lower_lati'])
        for i in range(3):
            for j in range(133):
                writer.writerow([left_upper_long+x*j, left_upper_lati+y*i, left_upper_long+x*j, left_upper_lati+y*(
                    i+1), left_upper_long+x*(j+1), left_upper_lati+y*i, left_upper_long+x*(j+1), left_upper_lati+y*(i+1)])


# read the image of the target and apply gaussian filter and canny detection to get the boundary
img = cv2.imread('solar.png', 0)
img = cv2.GaussianBlur(img, (3, 3), 0)
canny = cv2.Canny(img, 50, 720)

# make a mask and apply to the target image
mask = np.zeros(img.shape, dtype="uint8")
cv2.rectangle(mask, (500, 660), (2400, 800), (255, 255, 255), -1)
maskedImg = cv2.bitwise_and(canny, mask)

# use HoughLinesP to detect lines in the boundary and thus get four vertex of the boundary
lines = cv2.HoughLinesP(maskedImg, rho=1, theta=1*np.pi /
                        180, threshold=100, minLineLength=10, maxLineGap=2000)
N = lines.shape[0]
xlu = lines[1][0][0]
ylu = lines[1][0][1]
xrd = lines[1][0][2]
yrd = lines[1][0][3]
for i in range(N):
    x1 = lines[i][0][0]
    y1 = lines[i][0][1]
    x2 = lines[i][0][2]
    y2 = lines[i][0][3]
    xlu = min(x1, x2, xlu)
    ylu = min(y1, y2, ylu)
    xrd = max(x1, x2, xrd)
    yrd = max(y1, y2, yrd)

# control mouse to point at the left_upper point and right_lower point, then save the longitude and latitude image
m = PyMouse()
m.click(xlu, ylu)
time.sleep(1)
im = ImageGrab.grab(bbox=(1100, 1350, 1400, 1400))
im.save('lu.png')
m.click(xrd, yrd)
time.sleep(1)
m.click(xrd, yrd)
time.sleep(1)
im = ImageGrab.grab(bbox=(1100, 1350, 1400, 1400))
im.save('rl.png')

# use pytessertact to recognize the number in the image
loclu = pytesseract.image_to_string(Image.open('lu.png'))
locrl = pytesseract.image_to_string(Image.open('rl.png'))
loclu = loclu.replace('U', '0')
lu_lo, lu_la = loclu.split(',')
rl_lo, rl_la = locrl.split(',')
lu_lo = float(lu_lo)
lu_la = float(lu_la)
rl_lo = float(rl_lo)
rl_la = float(rl_la)

# use the number to calculate the location of each cell
returncvs(lu_lo, lu_la, lu_lo, rl_la, rl_lo, lu_la, rl_lo, rl_la)
