import json
from math import inf
import matplotlib.pyplot as plt
import numpy as np

def plotNumericFeatures(featureNames, cumul=True, xCoupling=None):
    featureNameIndex = 0
    featureNamesIter = iter(featureNames)
    neighbourTypeNames = ["+/- GroupMeetingWithSpec",
                          "swapSpec 2P",
                          "swap 2Days",
                          "swapSpec 2NBR P",
                          "swap 2CloseP Pairs",
                          "swapSpec 2DiagonalP",
                          "swapSpec SameDayP",
                          "swapSpec P Rand Days",
                          "add best day",
                          "remove best day",
                          "swap best specialist 2p",
                          "multiple swaps"]

    jsonDepths = open("statistics/depths.json", "r")
    depthsData = jsonDepths.read()
    depths = json.loads(depthsData)
    jsonDepths.close()
    fig, ax = plt.subplots(nrows=2, ncols=2)
    row_index = 0
    minX = inf
    for row in ax:
        col_index = 0
        for col in row:
            featureName = next(featureNamesIter)
            featuresFile = open("statistics/" + featureName + ".json", "r")
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

                numberOfChanges = len(data)
                minX = np.amin(data[:,0]) if np.amin(data[:,0]) < minX else minX
                maxX = np.amax(data[:,0])

                if xCoupling != None:
                    couplingSize = (maxX - minX) / xCoupling
                    coupledData = np.zeros((xCoupling, 2))

                    for couplingIndex in range(xCoupling):
                        coupledData[couplingIndex, 0] = minX + (couplingIndex + 0.5) * couplingSize
                        coupledData[couplingIndex, 1] = \
                            np.sum(data[np.logical_and(minX + couplingIndex * couplingSize <= data[:,0],
                                                       data[:,0] < minX + (couplingIndex + 1) * couplingSize)][:,1])
                    data = coupledData
                my_label = (str(numberOfChanges) + " " + neighbourTypeNames[neighbourType])
                ax[row_index, col_index].set_xlabel("seconds")
                if cumul:
                    cumulative = np.cumsum(data[:,1])
                    col.plot(data[:,0] - minX, cumulative, label=my_label, color="C" + str(neighbourType))
                else:
                    col.plot(data[:,0] - minX, data[:,1], label=my_label, color="C" + str(neighbourType))
                ax[row_index, col_index].set_title(featureName)
                ax[row_index, col_index].legend()
            for d in depths:
                if minX - d < 0:
                    ax[row_index, col_index].axvline(d - minX, 0, np.amax(data[:,1]), c="grey", linestyle="--")

            subtitle = "Cumulative neighbours generated through time" if cumul else 'Neighbours generated through time'
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