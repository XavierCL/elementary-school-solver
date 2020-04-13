import solver.neighbourGenerators.swapSpecialistTwoBestMeetings as swapSpecialistTwoBestMeetings
import solver.solutionInstance as solutionInstance

import numpy as np
import random

def swapSpecialistWorstToBestMeeting(self: solutionInstance.SolutionInstance):
    meetingIndices = np.where(self.meetByPeriodByDayByLocalBySubjectByGroup)
    meetingIndicesArray = np.swapaxes(np.array(meetingIndices), 0, 1)
    np.random.shuffle(meetingIndicesArray)

    if len(meetingIndices) == 0:
        return None

    worstGroup = meetingIndicesArray[0][0]
    worstSpecialist = meetingIndicesArray[0][1]
    worstLocal = meetingIndicesArray[0][2]
    worstDay = meetingIndicesArray[0][3]
    worstPeriod = meetingIndicesArray[0][4]

    meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
    meetByPeriodByDayByLocalBySubjectByGroup[worstGroup, worstSpecialist, worstLocal, worstDay, worstPeriod] = False

    bestCostWithoutWorstMeeting = solutionInstance.SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup).getTotalCost()

    for meetingIndex in range(1, len(meetingIndicesArray)):

        currentGroup = meetingIndicesArray[meetingIndex][0]
        currentSpecialist = meetingIndicesArray[meetingIndex][1]
        currentLocal = meetingIndicesArray[meetingIndex][2]
        currentDay = meetingIndicesArray[meetingIndex][3]
        currentPeriod = meetingIndicesArray[meetingIndex][4]

        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
        meetByPeriodByDayByLocalBySubjectByGroup[currentGroup, currentSpecialist, currentLocal, currentDay, currentPeriod] = False

        currentCostWithoutMeeting = solutionInstance.SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup).getTotalCost()

        if currentCostWithoutMeeting.lowerOrEqualTo(bestCostWithoutWorstMeeting) and random.choice([0, 1, 2]) > 0:
            bestCostWithoutWorstMeeting = currentCostWithoutMeeting

            worstGroup = currentGroup
            worstSpecialist = currentSpecialist
            worstLocal = currentLocal
            worstDay = currentDay
            worstPeriod = currentPeriod

    return swapSpecialistTwoBestMeetings.swapSpecialistTwoBestMeetingsUsingSpecificMeeting(self, worstGroup, worstSpecialist, worstLocal, worstDay, worstPeriod)