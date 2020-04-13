import solver.neighbourGenerators.swapSpecialistTwoNeighbourMeetings as swapSpecialistTwoNeighbourMeetings
import solver.neighbourGenerators.swapSpecialistTwoSameDayMeetings as swapSpecialistTwoSameDayMeetings

import solver.solutionInstance as solutionInstance

import numpy as np
import random

def multipleSwaps(self: solutionInstance.SolutionInstance):

    generators = [swapSpecialistTwoNeighbourMeetings.swapSpecialistTwoNeighbourPeriods, swapSpecialistTwoSameDayMeetings.swapSpecialistSameDayPeriods]

    neighbourChoice = random.choice([0, 0, 1])
    firstStep = generators[neighbourChoice](self)
    if firstStep == None:
        return None

    neighbourChoice = random.choice([0, 0, 1])
    return generators[neighbourChoice](firstStep)
    