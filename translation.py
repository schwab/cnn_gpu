import imutils
import numpy as mp
import argparse
import cv2


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image.")
args = vars(ap.parse_args())


image = cv2.imread(args["image"])
shifted = imutils.translate(image, 0, 100)
cv2.imshow("Shifted Down", shifted)
cv2.waitKey(0)
