import solver.solutionInstance as solutionInstance
import solver.solutionCost as solutionCost
from solver.neighbourGenerators.neighbourGenerator import NeighbourGenerator

import sys
import os
import time
import numpy as np
import random
import math
import json
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def getSolutionInstance(classesAndResources, msToSpend, initialTemperature, temperatureDecreaseRate, withStats=True):

    emptyMeets = np.zeros((len(classesAndResources.groups),
                           len(classesAndResources.specialists),
                           len(classesAndResources.locals),
                           classesAndResources.school.daysInCycle,
                           classesAndResources.school.periodsInDay)
                          ).astype(np.bool)
    initialSolution = solutionInstance.SolutionInstance(classesAndResources, emptyMeets)

    startTime = time.time() * 1000.
    return optimizeSolutionInstance(initialSolution, initialTemperature, temperatureDecreaseRate, lambda better: None, lambda: time.time() * 1000. < startTime + msToSpend, startTime)

def optimizeSolutionInstance(lastSolution: solutionInstance.SolutionInstance, initialTemperature, temperatureDecreaseRate, betterSolutionFoundCallback, shouldContinue, startTime):

    neighbourGenerator = NeighbourGenerator()

    bestSolution = lastSolution
    bestSolutionCost = bestSolution.getTotalCost()

    goodNeighbourStats = [[] for _ in range(neighbourGenerator.neighbourTypeCount)]
    equalNeighbourStats = [[] for _ in range(neighbourGenerator.neighbourTypeCount)]
    badNeighbourStats = [[] for _ in range(neighbourGenerator.neighbourTypeCount)]
    realBadNeighbourStats = [[] for _ in range(neighbourGenerator.neighbourTypeCount)]
    noNeighbourStats = [[] for _ in range(neighbourGenerator.neighbourTypeCount)]
    depthStats = []

    generatedNeighbours = 0
    noNeighbourGenerated = 0
    selectedGood = 0
    selectedEqual = 0
    selectedBad = 0
    depth = 0
    printTrace = False
    print(solutionCost.SolutionCost.getDisplayHeader())
    try:
        while shouldContinue() and depth <= neighbourGenerator.maxDepth:
            depthStats.append(time.time())
            temperature = initialTemperature
            lastSolutionCost = lastSolution.getTotalCost()
            while shouldContinue() and not lastSolutionCost.isPerfect(depth):
                (neighbourType, neighbourSolution) = neighbourGenerator.getNeighbour(lastSolution, depth)
                generatedNeighbours += 1
                if neighbourSolution == None:
                    noNeighbourGenerated += 1
                    noNeighbourStats[neighbourType].append(time.time())
                else:
                    neighbourCost = neighbourSolution.getTotalCost()
                    if neighbourCost.lowerOrEqualTo(lastSolutionCost):
                        if not neighbourCost.equalsTo(lastSolutionCost):
                            selectedGood += 1
                            goodNeighbourStats[neighbourType].append(time.time())
                            if not printTrace:
                                sys.stdout.flush()
                                sys.stdout.write(("\r" + neighbourCost.toString()))
                            elif neighbourCost.highestMagnitude() != lastSolutionCost.highestMagnitude() and printTrace:
                                print(neighbourCost.toString())

                        else:
                            equalNeighbourStats[neighbourType].append(time.time())
                            selectedEqual += 1

                        lastSolutionCost = neighbourCost
                        lastSolution = neighbourSolution

                        if neighbourCost.lowerOrEqualTo(bestSolutionCost):
                            bestSolutionCost = neighbourCost
                            bestSolution = neighbourSolution
                            betterSolutionFoundCallback(bestSolution)

                        temperature *= temperatureDecreaseRate
                    else:
                        if neighbourCost.magnitude() == lastSolutionCost.magnitude() and random.uniform(0, 1) <= \
                                math.e**(-(neighbourCost.highestMagnitude() -
                                           lastSolutionCost.highestMagnitude())/temperature):
                            badNeighbourStats[neighbourType].append(time.time())
                            
                            if neighbourCost.highestMagnitude() != lastSolutionCost.highestMagnitude():
                                if printTrace:
                                    print(neighbourCost.toString())
                                else:
                                    sys.stdout.flush()
                                    sys.stdout.write(("\r" + neighbourCost.toString()))


                            lastSolutionCost = neighbourCost
                            lastSolution = neighbourSolution
                            selectedBad += 1
                            temperature *= temperatureDecreaseRate
                        else:
                            realBadNeighbourStats[neighbourType].append(time.time())
            depth+=1
    except KeyboardInterrupt:
        pass

    with open("statistics/Good_neighbour_generated.json", "w") as outfile:
        outfile.write(json.dumps(goodNeighbourStats))
    with open("statistics/Equal_neighbour_generated.json", "w") as outfile:
        outfile.write(json.dumps(equalNeighbourStats))
    with open("statistics/Bad_neighbour_generated.json", "w") as outfile:
        outfile.write(json.dumps(badNeighbourStats))
    with open("statistics/Real_bad_neighbour_generated.json", "w") as outfile:
        outfile.write(json.dumps(realBadNeighbourStats))
    with open("statistics/No_neighbour_generated.json", "w") as outfile:
        outfile.write(json.dumps(noNeighbourStats))
    with open("statistics/depths.json", "w") as outfile:
        outfile.write(json.dumps(depthStats))

    if bestSolutionCost.isPerfect():
        print("\nOPTIMAL FOUND after " + str(time.time() * 1000. - startTime) + "ms\n")
    else:
        print("\nTIMED OUT after " + str(time.time() * 1000. - startTime) + "ms\n")

    print("Generated neighbours: " + str(generatedNeighbours))
    print("No neighbours: " + str(noNeighbourGenerated))
    print("Selected neighbours: " + str(selectedGood + selectedEqual + selectedBad))
    print("Bested neighbours: " + str(selectedGood))
    print("Equal neighbours: " + str(selectedEqual))
    print("Bad neighbours: " + str(selectedBad))

    return bestSolution