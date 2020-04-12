import solver.solutionInstance as solutionInstance

import numpy as np
import random

def addBestGroupSpecialistMeeting(self: solutionInstance.SolutionInstance):
    groupDeficits = self.classesAndResources.groupsNeeds - np.sum(self.meetByPeriodByDayBySpecialistByGroup, axis=(2, 3))
    maxDeficit = np.max(groupDeficits)

    if maxDeficit <= 0:
        return None

    maxDeficitIndices = np.where(groupDeficits == maxDeficit)

    comblingDeficit = random.randrange(0, len(maxDeficitIndices[0]))

    addingGroup = maxDeficitIndices[0][comblingDeficit]
    addingSpecialist = maxDeficitIndices[1][comblingDeficit]
    possibleLocals = np.array(list(self.classesAndResources.localsBySpecialistAndGroup[addingGroup][addingSpecialist]))

    # Encoding all hard constraints to select a free period
    freePeriods = np.all([np.sum(self.meetByPeriodByDayBySpecialistByGroup[addingGroup], axis=0) == 0,
                        np.all([np.sum(self.meetByPeriodByDayBySpecialistByGroup[:,addingSpecialist], axis=0) == 0, self.classesAndResources.specialistsFreePeriods[addingSpecialist]], axis=0),
                        np.any(np.sum(self.meetByPeriodByDayByLocalBySubjectByGroup, axis=(0, 1))[possibleLocals] == 0, axis=0)], axis=0)
    
    freePeriodIndices = np.where(freePeriods)

    if len(freePeriodIndices[0]) == 0:
        return None

    selectedFreePeriodIndex = random.randrange(0, len(freePeriodIndices[0]))

    freeDay = freePeriodIndices[0][selectedFreePeriodIndex]
    freePeriod = freePeriodIndices[1][selectedFreePeriodIndex]

    freeLocalIndices = np.where(self.meetByPeriodByDayByLocalBySubjectByGroup[addingGroup, addingSpecialist, :, freeDay, freePeriod][possibleLocals] == False)
    selectedLocalIndex = random.randrange(0, len(freeLocalIndices[0]))
    selectedLocal = possibleLocals[selectedLocalIndex]

    meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
    meetByPeriodByDayByLocalBySubjectByGroup[addingGroup,
                                                addingSpecialist,
                                                selectedLocal,
                                                freeDay,
                                                freePeriod] = True

    return solutionInstance.SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)