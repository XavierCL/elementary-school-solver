import solutionInstance
import time
import numpy as np
import random
import math
import json


def getSolutionInstance(classesAndResources, msToSpend, initialTemperature, temperatureDecreaseRate):

    emptyMeets = np.zeros((len(classesAndResources.groups), len(classesAndResources.specialists), len(classesAndResources.locals), classesAndResources.school.daysInCycle, classesAndResources.school.periodsInDay)).astype(np.bool)
    lastSolution = solutionInstance.SolutionInstance(classesAndResources, emptyMeets)
    bestSolution = lastSolution
    bestSolutionCost = bestSolution.getTotalCost()

    goodNeighbourStats = [[] for _ in range(bestSolution.neighbourTypeCount)]
    equalNeighbourStats = [[] for _ in range(bestSolution.neighbourTypeCount)]
    badNeighbourStats = [[] for _ in range(bestSolution.neighbourTypeCount)]
    realBadNeighbourStats = [[] for _ in range(bestSolution.neighbourTypeCount)]
    noNeighbourStats = [[] for _ in range(bestSolution.neighbourTypeCount)]
    depthStats = []

    generatedNeighbours = 0
    noNeighbourGenerated = 0
    selectedGood = 0
    selectedEqual = 0
    selectedBad = 0
    depth = 0
    startTime = time.time() * 1000.

    try:
        while time.time() * 1000. < startTime + msToSpend and depth <= lastSolution.maxDepth:
            depthStats.append(time.time())
            temperature = initialTemperature
            lastSolutionCost = lastSolution.getTotalCost()
            while time.time() * 1000. < startTime + msToSpend and not lastSolutionCost.isPerfect(depth):
                (neighbourType, neighbourSolution) = lastSolution.getNeighbour(depth)
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
                            if neighbourCost.highestMagnitude() != lastSolutionCost.highestMagnitude():
                                print(neighbourCost.toString())
                        else:
                            equalNeighbourStats[neighbourType].append(time.time())
                            selectedEqual += 1
                        lastSolutionCost = neighbourCost
                        lastSolution = neighbourSolution
                        bestSolutionCost = neighbourCost
                        bestSolution = neighbourSolution
                        temperature *= temperatureDecreaseRate
                    else:
                        if neighbourCost.magnitude() == lastSolutionCost.magnitude() and random.uniform(0, 1) <= \
                                math.e**(-(neighbourCost.highestMagnitude() - lastSolutionCost.highestMagnitude())/temperature):
                            badNeighbourStats[neighbourType].append(time.time())
                            
                            if neighbourCost.highestMagnitude() != lastSolutionCost.highestMagnitude():
                                print(neighbourCost.toString())
                            
                            lastSolutionCost = neighbourCost
                            lastSolution = neighbourSolution
                            selectedBad += 1
                            temperature *= temperatureDecreaseRate
                        else:
                            realBadNeighbourStats[neighbourType].append(time.time())
            depth+=1
    except KeyboardInterrupt:
        pass

    with open("Good_neighbour_generated.json", "w") as outfile:
        outfile.write(json.dumps(goodNeighbourStats))
    with open("Equal_neighbour_generated.json", "w") as outfile:
        outfile.write(json.dumps(equalNeighbourStats))
    with open("Bad_neighbour_generated.json", "w") as outfile:
        outfile.write(json.dumps(badNeighbourStats))
    with open("Real_bad_neighbour_generated.json", "w") as outfile:
        outfile.write(json.dumps(realBadNeighbourStats))
    with open("No_neighbour_generated.json", "w") as outfile:
        outfile.write(json.dumps(noNeighbourStats))
    with open("depths.json", "w") as outfile:
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