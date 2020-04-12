import solver.solutionInstance as solutionInstance

import numpy as np
import random

def addOrRemoveGroupMeetingWithSpecialist(self: solutionInstance.SolutionInstance):
    groupsNeeds = self.classesAndResources.groupsNeeds != 0
    whereNeeds = np.where(groupsNeeds)
    triggeredNeed = random.randrange(0, len(whereNeeds[0]))

    triggeredGroup = whereNeeds[0][triggeredNeed]
    triggeredSpecialist = whereNeeds[1][triggeredNeed]

    triggeredLocal = random.choice(
        self.classesAndResources.localListBySpecialistAndGroup[triggeredGroup][triggeredSpecialist])

    addingGroup = random.choice([True, False])
    if addingGroup:
        # These groups and specialist must not already meet
        groupAndSpecialistDoNotMeet = np.sum(
            self.meetByPeriodByDayByLocalBySubjectByGroup[triggeredGroup, triggeredSpecialist], axis=0) == 0
        # And the local must be free on that period
        localIsFree = np.sum(self.meetByPeriodByDayByLocalBySubjectByGroup[:, :, triggeredLocal], axis=(0, 1)) == 0

        possiblePeriods = np.where(np.logical_and(groupAndSpecialistDoNotMeet, localIsFree))
    else:
        # These groups and specialist must meet
        possiblePeriods = np.where(np.sum(
            self.meetByPeriodByDayByLocalBySubjectByGroup[triggeredGroup, triggeredSpecialist], axis=0) != 0)

    if len(possiblePeriods[0]) == 0:
        return None

    possiblePeriodIndex = random.randrange(0, len(possiblePeriods[0]))

    triggeredDay = possiblePeriods[0][possiblePeriodIndex]
    triggeredPeriod = possiblePeriods[1][possiblePeriodIndex]

    meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
    meetByPeriodByDayByLocalBySubjectByGroup[triggeredGroup,
                                                triggeredSpecialist,
                                                triggeredLocal,
                                                triggeredDay,
                                                triggeredPeriod] = addingGroup

    return solutionInstance.SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)