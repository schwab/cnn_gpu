from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import classification_report
from nn.conv.shallownet import ShallowNet
from keras.optimizers import SGD
from keras.datasets import cifar10
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np 
import argparse

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", required=True,
        help="path to output model")
args = vars(ap.parse_args())

print ("[INFO] loading CIFAR-10 data...")

# partition training and testing splits 75% for training 25% for test
((trainX, trainY) ,(testX, testY)) = cifar10.load_data()
trainX = trainX.astype("float") / 255.0
testX = testX.astype("float") / 255.0

lb = LabelBinarizer()


trainY = lb.fit_transform(trainY)
testY = lb.fit_transform(testY)
labelNames = ["airplane", "automobile", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck"]



#initialize the optimizer and model
print("[INFO] compiling model...")
opt = SGD(lr=0.01)
model = ShallowNet.build(width=32, height=32, depth=3, classes=10)
model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])

#train then network
print("[INFO] training network...")
H = model.fit(trainX, trainY, validation_data=(testX, testY), \
    batch_size=32, epochs=40, verbose=1)
# save the network to disk
print("[INFO] serializing network to %s..." % (args["model"]))
model.save(args["model"])

#evaluate the newtork
print("[INFO] evaluating network...")
predictions = model.predict(testX, batch_size=32)
print(classification_report(testY.argmax(axis=1), 
    predictions.argmax(axis=1), 
    target_names=labelNames))

plt.style.use("ggplot")
fig = plt.figure()
plt.plot(np.arange(0, 40), H.history["loss"], label="train_loss")
plt.plot(np.arange(0, 40), H.history["val_loss"], label="val_loss")
plt.plot(np.arange(0, 40), H.history["acc"], label="train_acc")
plt.plot(np.arange(0, 40), H.history["val_acc"], label="val_acc")
plt.title("Training Loss and Accuracy")
plt.xlabel("Epoch #")
plt.ylabel("Loss/Accuracy")
plt.legend()
plt.ioff()
fig.savefig('/root/src/data/CIFAR-10_results.png', bbox_inches="tight")
plt.show()


