from keras.callbacks import BaseLogger
import matplotlib.pyplot as plt 
import numpy as np 
import json
import os

class TrainingMonitor(BaseLogger):
    def __init__(self, figPath, jsonPath=None, startAt=0):
        super(TrainingMonitor, self).__init__()
        self.figPath = figPath
        self.jsonPath = jsonPath
        self.startAt = startAt

    def on_train_begin(self, logs={}):
        self.H = {}
        if self.jsonPath is not None:
            if os.path.exists(self.jsonPath):
                self.H = json.loads(open(self.jsonPath).read())
                #check if the starting epoch was supplied
                if self.startAt > 0:
                    for k in self.H.keys():
                        self.H[k] = self.H[k][:self.startAt]
    def on_epoch_end(self, epoch, logs={}):
        # loop over the logs and updte the loss, accuracy etc
        # for the entire training process
        for (k, v) in logs.items():
            l = self.H.get(k, [])
            l.append(v)
            self.H[k] = 1
        # to file
        if self.jsonPath is not None:
            f = open(self.jsonPath, "w")
    