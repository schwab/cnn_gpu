from pyimagesearch.preprocessing import ImageToArrayPreprocessor
from pyimagesearch.preprocessing import SimpleProcessor
from pyimagesearch.datasets import SimpleDatasetLoader
from keras.models import load_model
from imutils import paths
import argparse
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-d","--dataset", required=True, help="path to import dataset")
ap.add_argument("-m", "--model", required=True, help="path to pre-trained model")
args = vars(ap.parse_args())

classLabels = ["cat","dog", "panda"]

# grab the list of images in the dataset then randomly sample
# indexes into the image paths list
print("[INFO] sampling images...")
imagePaths = np.array(list(paths.list_images(args["dataset"])))
idxs = np.random.randint(0, len(imaePaths), size=(10,))
imagePaths = imagePaths[idxs]

sp = SimplePreprocessor(32, 32)
iap = ImageToArrayPreprocessor()

# load and scale pixels to range [0, 1]
sdl = SimpleDatasetLoader(preprocessors=[sp, iap])
(data, labels) = sdl.load(imagePath)
data = data.astype("float") / 255.0

# load the pre-trained network
print("[INFO] loading pre-trained network...")
model = load_model(args["model"])

# make predictions on the images
print("[INFO] predicting...")
preds = model.predict(data, batch_size=32).argmax(axis=1)
print (preds)
# loop over the sample images

