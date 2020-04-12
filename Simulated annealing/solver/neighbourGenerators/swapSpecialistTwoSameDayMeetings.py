import solver.solutionInstance as solutionInstance

import numpy as np
import random

def swapSpecialistSameDayPeriods(self: solutionInstance.SolutionInstance):
    groupWithSwappedSpecialist = random.randrange(0, self.meetByPeriodByDayByLocalBySubjectByGroup.shape[0])
    groupSpecialists = np.where(np.sum(
        self.meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist], axis=(1, 2, 3)) > 0)[0]

    if len(groupSpecialists) == 0:
        return None

    specialistWithSwappedGroup = random.choice(groupSpecialists)

    possibleFirstPeriods = np.where(
        self.meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist, specialistWithSwappedGroup])
    firstPeriodSwap = random.randrange(0, len(possibleFirstPeriods[0]))
    firstLocal = possibleFirstPeriods[0][firstPeriodSwap]
    firstDay = possibleFirstPeriods[1][firstPeriodSwap]
    firstPeriod = possibleFirstPeriods[2][firstPeriodSwap]

    possibleSecondPeriods = (np.arange(0, self.classesAndResources.school.periodsInDay - 1) + firstPeriod) % \
                            self.classesAndResources.school.periodsInDay

    possibleSecondPeriodsNotTeachingGroup = np.where(
        (np.sum(self.meetByPeriodByDayBySpecialistByGroup[:,
                specialistWithSwappedGroup, firstDay], axis=0) == 0)[possibleSecondPeriods])[0]
    possibleSecondPeriodsTeachingOtherGroups = np.where(
        np.concatenate([self.meetByPeriodByDayByLocalBySubjectByGroup[
                        :groupWithSwappedSpecialist,
                        specialistWithSwappedGroup,
                        firstLocal,
                        firstDay],
                        self.meetByPeriodByDayByLocalBySubjectByGroup[
                        groupWithSwappedSpecialist + 1:,
                        specialistWithSwappedGroup,
                        firstLocal,
                        firstDay]])[:, possibleSecondPeriods])

    if len(possibleSecondPeriodsNotTeachingGroup) + len(possibleSecondPeriodsTeachingOtherGroups[0]) == 0:
        return None

    secondPeriodSwap = random.randrange(0, len(possibleSecondPeriodsNotTeachingGroup) + len(
        possibleSecondPeriodsTeachingOtherGroups[0]))

    meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)

    if secondPeriodSwap < len(possibleSecondPeriodsNotTeachingGroup):
        selectedIndex = possibleSecondPeriodsNotTeachingGroup[secondPeriodSwap]
        secondDay = firstDay
        secondPeriod = possibleSecondPeriods[selectedIndex]

        meetByPeriodByDayByLocalBySubjectByGroup[
            groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal, firstDay, firstPeriod] = False
        meetByPeriodByDayByLocalBySubjectByGroup[
            groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal, secondDay, secondPeriod] = True

        return solutionInstance.SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)
    else:
        secondPeriodSwap -= len(possibleSecondPeriodsNotTeachingGroup)

        selectedIndex = possibleSecondPeriodsTeachingOtherGroups[1][secondPeriodSwap]
        secondGroup = possibleSecondPeriodsTeachingOtherGroups[0][secondPeriodSwap]
        secondDay = firstDay
        secondPeriod = possibleSecondPeriods[selectedIndex]

        # Need to recalibrate extracted group
        if secondGroup >= groupWithSwappedSpecialist:
            secondGroup += 1

        meetByPeriodByDayByLocalBySubjectByGroup[
            groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal, firstDay, firstPeriod] = False
        meetByPeriodByDayByLocalBySubjectByGroup[
            groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal, secondDay, secondPeriod] = True

        meetByPeriodByDayByLocalBySubjectByGroup[
            secondGroup, specialistWithSwappedGroup, firstLocal, firstDay, firstPeriod] = True
        meetByPeriodByDayByLocalBySubjectByGroup[
            secondGroup, specialistWithSwappedGroup, firstLocal, secondDay, secondPeriod] = False

        return solutionInstance.SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)