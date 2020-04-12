import solver.solutionInstance as solutionInstance

import numpy as np
import random

def removeBestGroupSpecialistMeeting(self: solutionInstance.SolutionInstance):
    groupOverflows = np.sum(self.meetByPeriodByDayBySpecialistByGroup, axis=(2, 3)) - self.classesAndResources.groupsNeeds
    maxOverflow = np.max(groupOverflows)

    if maxOverflow <= 0:
        return None

    overflowIndices = np.where(groupOverflows == maxOverflow)

    overflowIndex = random.randrange(0, len(overflowIndices[0]))

    removingGroup = overflowIndices[0][overflowIndex]
    removingSpecialist = overflowIndices[1][overflowIndex]

    groupAndSpecialistMeetingIndices = np.where(self.meetByPeriodByDayByLocalBySubjectByGroup[removingGroup, removingSpecialist])

    removingMeetingIndex = random.randrange(0, len(groupAndSpecialistMeetingIndices[0]))

    removingLocal = groupAndSpecialistMeetingIndices[0][removingMeetingIndex]
    removingDay = groupAndSpecialistMeetingIndices[1][removingMeetingIndex]
    removingPeriod = groupAndSpecialistMeetingIndices[2][removingMeetingIndex]

    meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
    meetByPeriodByDayByLocalBySubjectByGroup[removingGroup,
                                                removingSpecialist,
                                                removingLocal,
                                                removingDay,
                                                removingPeriod] = False

    return solutionInstance.SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)