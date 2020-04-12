import solver.solutionInstance as solutionInstance

import numpy as np
import random

def swapTwoDays(self):
    meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
    firstDay = random.randrange(0, meetByPeriodByDayByLocalBySubjectByGroup.shape[3])
    secondDay = random.randrange(0, meetByPeriodByDayByLocalBySubjectByGroup.shape[3] - 1)
    if secondDay >= firstDay:
        secondDay += 1
    meetByPeriodByDayByLocalBySubjectByGroup[...,[firstDay, secondDay],:] = \
        meetByPeriodByDayByLocalBySubjectByGroup[...,[secondDay, firstDay],:]
    return solutionInstance.SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)