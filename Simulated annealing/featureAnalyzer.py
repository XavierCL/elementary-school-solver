import zipfile
import json
import os
import random
import matplotlib.pyplot as plt
import numpy as np

def plotNumericFeatures(featureName, xCoupling=None):
    featuresFile = open(featureName + ".json", "r")
    featuresData = featuresFile.read()
    featuresFile.close()
    features = json.loads(featuresData)

    for neighbourType, times in enumerate(features):

        if len(times) == 0:
            continue

        data = np.zeros((len(times), 2))
        observationIndex = 0

        for timed in times:
            data[observationIndex, 0] = timed
            data[observationIndex, 1] = 1.
            observationIndex+=1

        if xCoupling != None:
            minX = np.amin(data[:,0])
            maxX = np.amax(data[:,0])
            couplingSize = (maxX - minX) / xCoupling

            coupledData = np.zeros((xCoupling, 2))

            for couplingIndex in range(xCoupling):
                coupledData[couplingIndex, 0] = minX + (couplingIndex + 0.5) * couplingSize
                coupledData[couplingIndex, 1] = np.sum(data[np.logical_and(minX + couplingIndex * couplingSize <= data[:,0], data[:,0] < minX + (couplingIndex + 1) * couplingSize)][:,1])

            data = coupledData

        plt.plot(data[:,0], data[:,1], "C" + str(neighbourType), label='Neighbour type ' + str(neighbourType))

plotNumericFeatures("goodNeighbourTypes",80)

plt.legend(loc="upper left")
plt.show()