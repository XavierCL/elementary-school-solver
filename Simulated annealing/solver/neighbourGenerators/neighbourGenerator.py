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

import solver.solutionInstance as solutionInstance

import random

def getNeighbour(self: solutionInstance.SolutionInstance, depth: int) -> (int, solutionInstance.SolutionInstance):
    neighbourFunctions = [addOrRemoveMeeting.addOrRemoveGroupMeetingWithSpecialist,
                    swapSpecialistTwoRandomMeetings.swapSpecialistTwoPeriods,
                    swapTwoDays.swapTwoDays,
                    swapSpecialistTwoNeighbourMeetings.swapSpecialistTwoNeighbourPeriods,
                    swapSpecialistTwoCloseMeetingPairs.swapTwoClosePeriodsPairs,
                    swapSpecialistTwoDiagonalMeetings.swapSpecialistTwoDiagonalNeighbourPeriods,
                    swapSpecialistTwoSameDayMeetings.swapSpecialistSameDayPeriods,
                    swapSpecialistTwoDaysAppartMeetings.swapSpecialistPeriodsRndDaysApart,
                    addBestGroupSpecialistMeeting.addBestGroupSpecialistMeeting,
                    removeBestGroupSpecialistMeeting.removeBestGroupSpecialistMeeting,
                    swapSpecialistTwoBestMeetings.swapSpecialistTwoBestMeetings]

    if depth == 0:
        neighbourChoice = random.choice([0, 1, 2, 3, 6, 8, 9, 10])
        return (neighbourChoice, neighbourFunctions[neighbourChoice](self))

    elif depth == 1:
        neighbourChoice = random.choice([1, 3, 5, 6, 7, 10])
        return (neighbourChoice, neighbourFunctions[neighbourChoice](self))
    else:
        # At depth > 1, must generate period moving only moves, that are consistent with the locals' constraints
        neighbourChoice = random.choice([1, 3, 5, 6, 7, 10])
        return (neighbourChoice, neighbourFunctions[neighbourChoice](self))