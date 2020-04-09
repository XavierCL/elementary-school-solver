import json
import matplotlib.pyplot as plt
import numpy as np

def plotNumericFeatures(featureNames, cumul=True, xCoupling=None):
    featureNameIndex = 0
    neighbourTypeNames = ["+/- meeting w/ specialist",
                          "swap rnd P",
                          "swap rnd days",
                          "swap adjacent P",
                          "swap close P",
                          "swap diagonal P",
                          "swap P in same day",
                          "swap P from rnd days",
                          "multiple swaps"]

    fig, ax = plt.subplots(nrows=2, ncols=2)
    row_index = 0
    for row in ax:
        col_index = 0
        for col in row:
            featureName = featureNames[featureNameIndex]
            featuresFile = open(featureName + ".json", "r")
            featuresData = featuresFile.read()
            featuresFile.close()
            features = json.loads(featuresData)
            featureNameIndex += 1

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
                        coupledData[couplingIndex, 1] = \
                            np.sum(data[np.logical_and(minX + couplingIndex * couplingSize <= data[:,0],
                                                       data[:,0] < minX + (couplingIndex + 1) * couplingSize)][:,1])
                    numberOfChanges = len(data)
                    data = coupledData
                my_label = (str(numberOfChanges) + " " + neighbourTypeNames[neighbourType])
                ax[row_index, col_index].set_xlabel("seconds")
                if cumul:
                    cumulative = np.cumsum(data[:,1])
                    col.plot(data[:,0] - minX, cumulative, label=my_label)
                else:
                    col.plot(data[:,0] - minX, data[:,1], label=my_label)
                ax[row_index, col_index].set_title(featureName)
                ax[row_index, col_index].legend()
            subtitle = "Cumulative total of neighbours generated through time" if cumul else 'Neighbours generated through time'
            fig.suptitle(subtitle)
            col_index += 1
        row_index += 1


featureNames = ["Real_bad_neighbour_generated",
                "Bad_neighbour_generated",
                "Equal_neighbour_generated",
                "Good_neighbour_generated"]
cumulativeDisplay = True
plotNumericFeatures(featureNames, cumulativeDisplay)
plt.show()