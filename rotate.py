import numpy as np
import argparse
import imutils
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to image")
args = vars(ap.parse_args())

image=cv2.imread(args["image"])
rotated = imutils.rotate(image, 180)
cv2.imshow("Rotated by 180 Degress", rotated)
cv2.waitKey(0)