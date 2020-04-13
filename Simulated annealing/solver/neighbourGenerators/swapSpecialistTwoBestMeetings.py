import solver.solutionInstance as solutionInstance

import numpy as np
import random

def swapSpecialistTwoBestMeetingsUsingSpecificMeeting(self: solutionInstance.SolutionInstance, group, specialist, local, day, period):
    possibleSecondPeriodsNotTeachingGroup = np.where(
        np.sum(self.meetByPeriodByDayByLocalBySubjectByGroup[:, specialist], axis=(0, 1)) == 0)
    possibleSecondPeriodsTeachingOtherGroups = np.where(
        np.concatenate([self.meetByPeriodByDayByLocalBySubjectByGroup[:group,
                        specialist,
                        local],
                        self.meetByPeriodByDayByLocalBySubjectByGroup[group + 1:,
                        specialist,
                        local]]))
    if len(possibleSecondPeriodsNotTeachingGroup[0]) + len(possibleSecondPeriodsTeachingOtherGroups[0]) == 0:
        return None

    bestSwap = self
    bestSwapCost = self.getTotalCost()

    shuffledIndices = list(range(len(possibleSecondPeriodsNotTeachingGroup[0]) + len(possibleSecondPeriodsTeachingOtherGroups[0])))
    random.shuffle(shuffledIndices)

    for secondPeriodSwap in shuffledIndices:
        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)

        if secondPeriodSwap < len(possibleSecondPeriodsNotTeachingGroup[0]):

            secondDay = possibleSecondPeriodsNotTeachingGroup[0][secondPeriodSwap]
            secondPeriod = possibleSecondPeriodsNotTeachingGroup[1][secondPeriodSwap]

            meetByPeriodByDayByLocalBySubjectByGroup[group,
                                                        specialist,
                                                        local,
                                                        day,
                                                        period] = False
            meetByPeriodByDayByLocalBySubjectByGroup[group,
                                                        specialist,
                                                        local,
                                                        secondDay,
                                                        secondPeriod] = True

            currentSwap = solutionInstance.SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)
        else:
            secondPeriodSwap -= len(possibleSecondPeriodsNotTeachingGroup[0])

            secondGroup = possibleSecondPeriodsTeachingOtherGroups[0][secondPeriodSwap]

            # Need to recalibrate extracted group
            if secondGroup >= group:
                secondGroup += 1

            secondDay = possibleSecondPeriodsTeachingOtherGroups[1][secondPeriodSwap]
            secondPeriod = possibleSecondPeriodsTeachingOtherGroups[2][secondPeriodSwap]

            meetByPeriodByDayByLocalBySubjectByGroup[group, specialist,
                                                        local, day, period] = False
            meetByPeriodByDayByLocalBySubjectByGroup[group, specialist,
                                                        local, secondDay, secondPeriod] = True

            meetByPeriodByDayByLocalBySubjectByGroup[secondGroup, specialist,
                                                        local, day, period] = True
            meetByPeriodByDayByLocalBySubjectByGroup[secondGroup, specialist,
                                                        local, secondDay, secondPeriod] = False

            currentSwap = solutionInstance.SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

        currentSwapCost = currentSwap.getTotalCost()

        if currentSwapCost.lowerOrEqualTo(bestSwapCost) and random.choice([0, 1, 2]) > 0:
            bestSwap = currentSwap
            bestSwapCost = currentSwapCost

    if bestSwap is self:
        return None

    return bestSwap

def swapSpecialistTwoBestMeetings(self: solutionInstance.SolutionInstance):
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

    return swapSpecialistTwoBestMeetingsUsingSpecificMeeting(self, groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal, firstDay, firstPeriod)