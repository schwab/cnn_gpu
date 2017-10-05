from keras.models import Sequential
from keras.layers.convolution import Conv2D
from keras.layers.convolution import MaxPooling2D
from keras.layers.core import Activation
from keras.layers.core import Flatten
from keras.layers.core import Dense
from keras import backend as K

class LeNet:
@staticmethod
def build(width, height, depth, classes):
    # initialize the model
    model = Sequential()
    inputShape = (height, width, depth)

    # if we are using "channels first" udpate the input shape
    if K.image_data_format() == "channels_first":
        inputShape = (depth, height, width)