import solver.solutionInstance as solutionInstance

import numpy as np
import random

def swapTwoClosePeriodsPairs(self: solutionInstance.SolutionInstance): # Turned out not to be a good neighbour generator
    meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
    firstDay = random.randrange(0, meetByPeriodByDayByLocalBySubjectByGroup.shape[3])
    secondDay = random.randrange(0, meetByPeriodByDayByLocalBySubjectByGroup.shape[3])
    firstPeriod = random.choice(list(range(self.classesAndResources.school.periodsInAm - 1)) +
                                list(map(lambda pmPeriod: self.classesAndResources.school.periodsInAm + pmPeriod,
                                            range(self.classesAndResources.school.periodsInPm - 1))))

    secondPeriodAmChoice = list(range(self.classesAndResources.school.periodsInAm - 1))
    secondPeriodPmChoice = list(map(lambda pmPeriod: self.classesAndResources.school.periodsInAm + pmPeriod,
                                    range(self.classesAndResources.school.periodsInPm - 1)))

    if firstDay == secondDay:
        if firstPeriod < self.classesAndResources.school.periodsInAm:
            del secondPeriodAmChoice[firstPeriod]
            if firstPeriod < len(secondPeriodAmChoice):
                del secondPeriodAmChoice[firstPeriod]
        else:
            del secondPeriodPmChoice[firstPeriod - len(secondPeriodAmChoice) - 1]
            if firstPeriod - len(secondPeriodAmChoice) - 1 < len(secondPeriodPmChoice):
                del secondPeriodPmChoice[firstPeriod - len(secondPeriodAmChoice) - 1]

    secondPeriod = random.choice(secondPeriodAmChoice + secondPeriodPmChoice)
    
    meetByPeriodByDayByLocalBySubjectByGroup[...,[firstDay, firstDay, secondDay, secondDay],
                                                [firstPeriod, firstPeriod + 1, secondPeriod, secondPeriod + 1]] = \
        meetByPeriodByDayByLocalBySubjectByGroup[...,[secondDay, secondDay, firstDay, firstDay],
                                                    [secondPeriod, secondPeriod + 1, firstPeriod, firstPeriod + 1]]
    return solutionInstance.SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)