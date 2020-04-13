import solver.neighbourGenerators.addOrRemoveMeeting as addOrRemoveMeeting
import solver.neighbourGenerators.swapSpecialistTwoRandomMeetings as swapSpecialistTwoRandomMeetings
import solver.neighbourGenerators.swapTwoDays as swapTwoDays
import solver.neighbourGenerators.swapSpecialistTwoNeighbourMeetings as swapSpecialistTwoNeighbourMeetings
import solver.neighbourGenerators.swapSpecialistTwoCloseMeetingPairs as swapSpecialistTwoCloseMeetingPairs
import solver.neighbourGenerators.swapSpecialistTwoDiagonalMeetings as swapSpecialistTwoDiagonalMeetings
import solver.neighbourGenerators.swapSpecialistTwoSameDayMeetings as swapSpecialistTwoSameDayMeetings
import solver.neighbourGenerators.swapSpecialistTwoDaysAppartMeetings as swapSpecialistTwoDaysAppartMeetings
import solver.neighbourGenerators.addBestGroupSpecialistMeeting as addBestGroupSpecialistMeeting
import solver.neighbourGenerators.removeBestGroupSpecialistMeeting as removeBestGroupSpecialistMeeting
import solver.neighbourGenerators.swapSpecialistTwoBestMeetings as swapSpecialistTwoBestMeetings
import solver.neighbourGenerators.multipleSwaps as multipleSwaps

import solver.solutionInstance as solutionInstance

import random

class NeighbourGenerator:

    def __init__(self):
        self.neighbourFunctions = [addOrRemoveMeeting.addOrRemoveGroupMeetingWithSpecialist,
            swapSpecialistTwoRandomMeetings.swapSpecialistTwoPeriods,
            swapTwoDays.swapTwoDays,
            swapSpecialistTwoNeighbourMeetings.swapSpecialistTwoNeighbourPeriods,
            swapSpecialistTwoCloseMeetingPairs.swapTwoClosePeriodsPairs,
            swapSpecialistTwoDiagonalMeetings.swapSpecialistTwoDiagonalNeighbourPeriods,
            swapSpecialistTwoSameDayMeetings.swapSpecialistSameDayPeriods,
            swapSpecialistTwoDaysAppartMeetings.swapSpecialistPeriodsRndDaysApart,
            addBestGroupSpecialistMeeting.addBestGroupSpecialistMeeting,
            removeBestGroupSpecialistMeeting.removeBestGroupSpecialistMeeting,
            swapSpecialistTwoBestMeetings.swapSpecialistTwoBestMeetings,
            multipleSwaps.multipleSwaps]

        self.neighbourTypeCount = len(self.neighbourFunctions)
        self.depthGenerators = [self.getDepthZeroNeighbour,
            self.getDepthOneNeighbour,
            self.getDepthTwoNeighbour]
        self.maxDepth = len(self.depthGenerators)

    def getNeighbour(self, solutionInstance: solutionInstance.SolutionInstance, depth: int) -> (int, solutionInstance.SolutionInstance):
        return self.depthGenerators[depth](solutionInstance)

    def getDepthZeroNeighbour(self, solutionInstance: solutionInstance.SolutionInstance):
        neighbourChoice = random.choice([1, 2, 3, 6, 8, 9] * 6 + [10])
        return (neighbourChoice, self.neighbourFunctions[neighbourChoice](solutionInstance))

    def getDepthOneNeighbour(self, solutionInstance: solutionInstance.SolutionInstance):
        neighbourChoice = random.choice([1, 3, 5, 6, 7, 11] * 6 + [10])
        return (neighbourChoice, self.neighbourFunctions[neighbourChoice](solutionInstance))

    def getDepthTwoNeighbour(self, solutionInstance: solutionInstance.SolutionInstance):
        # At depth > 1, must generate period moving only moves, that are consistent with the locals' constraints
        neighbourChoice = random.choice([1, 3, 5, 6, 7, 11] * 6 + [10])
        return (neighbourChoice, self.neighbourFunctions[neighbourChoice](solutionInstance))