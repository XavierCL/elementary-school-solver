from math import floor
from solver.solutionCost import SolutionCost
import random
import numpy as np

class SolutionInstance:

    def __init__(self, classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup):
        self.classesAndResources = classesAndResources
        self.meetByPeriodByDayByLocalBySubjectByGroup = meetByPeriodByDayByLocalBySubjectByGroup
        self.meetByPeriodByDayBySpecialistByGroup = np.sum(self.meetByPeriodByDayByLocalBySubjectByGroup, axis=2) != 0

        self.maxDepth = 2
        self.neighbourTypeCount = 9

    def assignGroupToSpecialistDayAndPeriod(self, specialist, day, period, local, oldGroupId, newGroupId):
        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
        meetByPeriodByDayByLocalBySubjectByGroup[[oldGroupId, newGroupId], specialist, local, day, period] = meetByPeriodByDayByLocalBySubjectByGroup[[newGroupId, oldGroupId], specialist, local, day, period]
        
        return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def assignLocalToSpecialistDayAndPeriod(self, specialist, day, period, group, oldLocalId, newLocalId):
        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
        meetByPeriodByDayByLocalBySubjectByGroup[group, specialist, [oldLocalId, newLocalId], day, period] = meetByPeriodByDayByLocalBySubjectByGroup[group, specialist, [newLocalId, oldLocalId], day, period]
        
        return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def removeSpecialistDayPeriodMeeting(self, specialist, day, period):
        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
        meetByPeriodByDayByLocalBySubjectByGroup[:, specialist, :, day, period] = False
        
        return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def addSpecialistDayPeriodMeetingWithGroupAtLocal(self, specialist, day, period, group, local):
        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
        meetByPeriodByDayByLocalBySubjectByGroup[group, specialist, local, day, period] = True
        
        return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def getTotalCost(self):
        hardConstraintViolationCount = self.getHardConstraintCost()
        customHardCost = self.classesAndResources.getDepthCost(self, 0)

        meetArgs = np.where(self.meetByPeriodByDayByLocalBySubjectByGroup)

        premiseConstraintViolationCount = self.getPremiseConstraintCost(meetArgs)
        customPremiseCost = self.classesAndResources.getDepthCost(self, 1)

        (softiesConstraintViolationCount, softiesDetails) = self.getSoftConstraintCost(meetArgs)
        customSoftCost = self.classesAndResources.getDepthCost(self, 2)

        return SolutionCost(np.asarray([hardConstraintViolationCount + customHardCost, premiseConstraintViolationCount + customPremiseCost, softiesConstraintViolationCount + customSoftCost]), softiesDetails)

    def getHardConstraintCost(self):
        hardConstraintViolationCount = 0
        hardConstraintViolationCount += self.groupNeedsHardConstraintViolationCost()
        hardConstraintViolationCount += self.singleSpecialistByGroupPeriodViolationCost()
        hardConstraintViolationCount += self.singleGroupByFreeSpecialistPeriodViolationCost()
        hardConstraintViolationCount += self.singleLocalOccupancyViolationCost()

        # Locals only see groups and specialists they are supposed to
        # Expected not to happen by neighbour generation

        return hardConstraintViolationCount

    def groupNeedsHardConstraintViolationCost(self):
        # Every group need has been fulfilled
        return np.sum(np.abs(np.sum(self.meetByPeriodByDayBySpecialistByGroup, axis=(2, 3)) - self.classesAndResources.groupsNeeds))

    def singleSpecialistByGroupPeriodViolationCost(self):
        # No groups see a specialist twice at the same period
        return np.sum(np.sum(self.meetByPeriodByDayBySpecialistByGroup, axis=1) > 1)

    def singleGroupByFreeSpecialistPeriodViolationCost(self):
        # No specialists see more than a group when they are free
        specialistMeetDiffWithFreePeriods = np.sum(self.meetByPeriodByDayBySpecialistByGroup, axis=0) - self.classesAndResources.specialistsFreePeriods
        return np.sum(specialistMeetDiffWithFreePeriods[specialistMeetDiffWithFreePeriods > 0])

    def singleLocalOccupancyViolationCost(self):
        # No local see people twice at the same period
        return np.sum(np.sum(self.meetByPeriodByDayByLocalBySubjectByGroup, axis=(0, 1)) > 1)

    def getPremiseConstraintCost(self, meetArgs):

        premiseConstraintViolationCount = 0

        # Two different premises cannot be one period after the other (except at noon)
        meetByPeriodByDayByPremiseBySpecialist = np.zeros((self.meetByPeriodByDayByLocalBySubjectByGroup.shape[1], self.classesAndResources.premiseCount, self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3], self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4])).astype(np.bool)
        meetByPeriodByDayByPremiseBySpecialist[meetArgs[1], self.classesAndResources.premiseByLocal[meetArgs[2]], meetArgs[3], meetArgs[4]] = True
        for firstClosePeriod in range(self.classesAndResources.school.periodsInAm - 1):
            premiseConstraintViolationCount += np.sum(np.sum(np.sum(meetByPeriodByDayByPremiseBySpecialist[...,firstClosePeriod:firstClosePeriod+2], axis=3) >= 1, axis=1) > 1)
        for firstClosePeriod in range(self.classesAndResources.school.periodsInPm - 1):
            firstClosePeriod += self.classesAndResources.school.periodsInAm
            premiseConstraintViolationCount += np.sum(np.sum(np.sum(meetByPeriodByDayByPremiseBySpecialist[...,firstClosePeriod:firstClosePeriod+2], axis=3) >= 1, axis=1) > 1)

        return premiseConstraintViolationCount

    def getSoftConstraintCost(self, meetArgs):
        tutorFreePeriodsAcrossTheDaysCost = self.getTutorFreePeriodsAcrossDaysCost()
        tutorFreePeriodsAcrossThePeriodsCost = self.getTutorFreePeriodsAcrossPeriodsCost()
        tutorFreePeriodsAcrossTheBoard = self.getTutorFreePeriodsAcrossTheBoardCost()
        # groupsSubjectPeriodsAcrossTheDaysCost = self.getGroupsSubjectsAcrossTheDaysCost()
        groupsSubjectPeriodsAcrossThePeriodsCost = self.getGroupsSubjectsAcrossThePeriodsCost()
        groupsSubjectPeriodsAcrossTheBoardCost = self.getGroupsSubjectsAcrossTheBoardCost()
        teachSameLevelsTogetherCost = self.getTeachSameLevelsTogetherCost(meetArgs)

        return ((tutorFreePeriodsAcrossTheDaysCost * 1000 +
                 tutorFreePeriodsAcrossThePeriodsCost * 10 +
                 tutorFreePeriodsAcrossTheBoard +
                 groupsSubjectPeriodsAcrossThePeriodsCost * 10 +
                 groupsSubjectPeriodsAcrossTheBoardCost * 10 +
                 teachSameLevelsTogetherCost * 1000
                 ) / 1_500_000,
                [tutorFreePeriodsAcrossTheDaysCost,
                 tutorFreePeriodsAcrossThePeriodsCost,
                 tutorFreePeriodsAcrossTheBoard,
                 groupsSubjectPeriodsAcrossThePeriodsCost,
                 groupsSubjectPeriodsAcrossTheBoardCost,
                 teachSameLevelsTogetherCost])

    def getTutorFreePeriodsAcrossDaysCost(self):
        # Disperse a tutor free periods across the days
        meetByPeriodByDayByGroup = np.sum(self.meetByPeriodByDayBySpecialistByGroup, axis=1)
        meetArgsByPeriodByDayByGroup = np.where(meetByPeriodByDayByGroup)
        daysByGroup = meetArgsByPeriodByDayByGroup[1]
        shiftedDaysByGroup = np.roll(daysByGroup, 1)
        groups = meetArgsByPeriodByDayByGroup[0]
        shiftedGroups = np.roll(groups, 1)
        groupsStarts = groups != shiftedGroups
        groupsWhereStarts = np.where(groupsStarts)[0]
        shiftedGroupsWhereStarts = np.roll(groupsWhereStarts, -1)
        shiftedDaysByGroup[groupsWhereStarts] = shiftedDaysByGroup[shiftedGroupsWhereStarts] - self.classesAndResources.school.daysInCycle
        return np.sum((daysByGroup - shiftedDaysByGroup).astype(np.float64)**4)

    def getTutorFreePeriodsAcrossPeriodsCost(self):
        # Disperse a tutor free periods across the periods
        meetByDayByPeriodByGroup = np.swapaxes(np.sum(self.meetByPeriodByDayBySpecialistByGroup, axis=1), 1, 2)
        meetArgsByDayByPeriodByGroup = np.where(meetByDayByPeriodByGroup)
        periodsByGroup = meetArgsByDayByPeriodByGroup[1]
        shiftedPeriodsByGroup = np.roll(periodsByGroup, 1)
        groups = meetArgsByDayByPeriodByGroup[0]
        shiftedGroups = np.roll(groups, 1)
        groupsStarts = groups != shiftedGroups
        groupsWhereStarts = np.where(groupsStarts)[0]
        shiftedGroupsWhereStarts = np.roll(groupsWhereStarts, -1)
        shiftedPeriodsByGroup[groupsWhereStarts] = shiftedPeriodsByGroup[shiftedGroupsWhereStarts] - self.classesAndResources.school.periodsInDay
        return np.sum((periodsByGroup - shiftedPeriodsByGroup).astype(np.float64)**3)

    def getTutorFreePeriodsAcrossTheBoardCost(self):
        # Disperse a tutor free periods across the board
        meetByDayAndPeriodByGroup = np.sum(self.meetByPeriodByDayBySpecialistByGroup, axis=1).reshape(self.meetByPeriodByDayBySpecialistByGroup.shape[0], -1)
        meetArgsByDayAndPeriodByGroup = np.where(meetByDayAndPeriodByGroup)
        daysAndPeriodsByGroup = meetArgsByDayAndPeriodByGroup[1]
        shiftedDaysAndPeriodsByGroup = np.roll(daysAndPeriodsByGroup, 1)
        groups = meetArgsByDayAndPeriodByGroup[0]
        shiftedGroups = np.roll(groups, 1)
        groupsStarts = groups != shiftedGroups
        groupsWhereStarts = np.where(groupsStarts)[0]
        shiftedGroupsWhereStarts = np.roll(groupsWhereStarts, -1)
        shiftedDaysAndPeriodsByGroup[groupsWhereStarts] = shiftedDaysAndPeriodsByGroup[shiftedGroupsWhereStarts] - (self.classesAndResources.school.periodsInDay * self.classesAndResources.school.daysInCycle)
        return np.sum((daysAndPeriodsByGroup - shiftedDaysAndPeriodsByGroup).astype(np.float64)**3)

    def getGroupsSubjectsAcrossTheDaysCost(self):
        # Disperse a group's single subject across the days
        meetByPeriodByDayBySpecialistAndGroup = self.meetByPeriodByDayBySpecialistByGroup.reshape((-1, self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3], self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4]))
        meetArgsByPeriodByDayBySpecialistAndGroup = np.where(meetByPeriodByDayBySpecialistAndGroup)
        daysBySpecialistAndGroup = meetArgsByPeriodByDayBySpecialistAndGroup[1]
        shiftedDaysBySpecialistAndGroup = np.roll(daysBySpecialistAndGroup, 1)
        specialistsAndGroups = meetArgsByPeriodByDayBySpecialistAndGroup[0]
        shiftedSpecialistsAndGroups = np.roll(specialistsAndGroups, 1)
        specialistsAndGroupsStarts = specialistsAndGroups != shiftedSpecialistsAndGroups
        specialistsAndGroupsWhereStarts = np.where(specialistsAndGroupsStarts)[0]
        shiftedSpecialistsAndGroupsWhereStarts = np.roll(specialistsAndGroupsWhereStarts, -1)
        shiftedDaysBySpecialistAndGroup[specialistsAndGroupsWhereStarts] = shiftedDaysBySpecialistAndGroup[shiftedSpecialistsAndGroupsWhereStarts] - self.classesAndResources.school.daysInCycle
        return np.sum((daysBySpecialistAndGroup - shiftedDaysBySpecialistAndGroup).astype(np.float64)**4)

    def getGroupsSubjectsAcrossThePeriodsCost(self):
        # Disperse a group's single subject across the periods
        meetByDayByPeriodBySpecialistAndGroup = np.swapaxes(self.meetByPeriodByDayBySpecialistByGroup, 2, 3).reshape((-1, self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4], self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3]))
        meetArgsByDayByPeriodBySpecialistAndGroup = np.where(meetByDayByPeriodBySpecialistAndGroup)
        periodsBySpecialistAndGroup = meetArgsByDayByPeriodBySpecialistAndGroup[1]
        shiftedPeriodsBySpecialistAndGroup = np.roll(periodsBySpecialistAndGroup, 1)
        specialistsAndGroups = meetArgsByDayByPeriodBySpecialistAndGroup[0]
        shiftedSpecialistsAndGroups = np.roll(specialistsAndGroups, 1)
        specialistsAndGroupsStarts = specialistsAndGroups != shiftedSpecialistsAndGroups
        specialistsAndGroupsWhereStarts = np.where(specialistsAndGroupsStarts)[0]
        shiftedSpecialistsAndGroupsWhereStarts = np.roll(specialistsAndGroupsWhereStarts, -1)
        shiftedPeriodsBySpecialistAndGroup[specialistsAndGroupsWhereStarts] = shiftedPeriodsBySpecialistAndGroup[shiftedSpecialistsAndGroupsWhereStarts] - self.classesAndResources.school.periodsInDay
        return np.sum((periodsBySpecialistAndGroup - shiftedPeriodsBySpecialistAndGroup).astype(np.float64)**3)

    def getGroupsSubjectsAcrossTheBoardCost(self):
        # Disperse a group's single subject across the board
        meetByDayAndPeriodBySpecialistAndGroup = self.meetByPeriodByDayBySpecialistByGroup.reshape(
            self.meetByPeriodByDayBySpecialistByGroup.shape[0] * self.meetByPeriodByDayBySpecialistByGroup.shape[1], -1)
        meetArgsByDayAndPeriodBySpecialistAndGroup = np.where(meetByDayAndPeriodBySpecialistAndGroup)
        daysAndPeriodsBySpecialistAndGroup = meetArgsByDayAndPeriodBySpecialistAndGroup[1]
        shiftedDaysAndPeriodsBySpecialistAndGroup = np.roll(daysAndPeriodsBySpecialistAndGroup, 1)
        specialistsAndGroups = meetArgsByDayAndPeriodBySpecialistAndGroup[0]
        shiftedSpecialistAndGroup = np.roll(specialistsAndGroups, 1)
        specialistsAndGroupsStarts = specialistsAndGroups != shiftedSpecialistAndGroup
        specialistsAndGroupsWhereStarts = np.where(specialistsAndGroupsStarts)[0]
        shiftedSpecialistsAndGroupsWhereStarts = np.roll(specialistsAndGroupsWhereStarts, -1)
        shiftedDaysAndPeriodsBySpecialistAndGroup[specialistsAndGroupsWhereStarts] = \
            shiftedDaysAndPeriodsBySpecialistAndGroup[shiftedSpecialistsAndGroupsWhereStarts] - \
            (self.classesAndResources.school.periodsInDay * self.classesAndResources.school.daysInCycle)
        return np.sum((daysAndPeriodsBySpecialistAndGroup -
                       shiftedDaysAndPeriodsBySpecialistAndGroup).astype(np.float64)**3)

    def getTeachSameLevelsTogetherCost(self, meetArgs):
        # Group together same years for specialists
        groupTogetherSameYearCost = 0.
        levelByPeriodByDayBySpecialist = np.ones((self.meetByPeriodByDayByLocalBySubjectByGroup.shape[1],
                                                  self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3],
                                                  self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4])) * \
                                         self.classesAndResources.maxLevel
        levelByPeriodByDayBySpecialist[meetArgs[1], meetArgs[3], meetArgs[4]] = \
            self.classesAndResources.levelByGroup[meetArgs[0]]
        for firstClosePeriod in range(self.classesAndResources.school.periodsInAm - 1):
            groupTogetherSameYearCost += np.sum(levelByPeriodByDayBySpecialist[..., firstClosePeriod] !=
                                                levelByPeriodByDayBySpecialist[..., firstClosePeriod + 1])
        for firstClosePeriod in range(self.classesAndResources.school.periodsInPm - 1):
            firstClosePeriod += self.classesAndResources.school.periodsInAm
            groupTogetherSameYearCost += np.sum(levelByPeriodByDayBySpecialist[..., firstClosePeriod] !=
                                                levelByPeriodByDayBySpecialist[..., firstClosePeriod + 1])
        return groupTogetherSameYearCost**2

    def getNeighbour(self, depth):
        if depth == 0:
            neighbourChoice = random.choice([0, 1, 2, 3, 6, 7])
            if neighbourChoice == 0:
                # Mandatory neighbour choice, adds the right classes, but still generates goods
                return (0, self.addOrRemoveGroupMeetingWithSpecialist())
            elif neighbourChoice == 1:
                # good neighbour choice
                return (1, self.swapSpecialistTwoPeriods())
            elif neighbourChoice == 2:
                # Poor neighbour choice, but still generates goods
                return (2, self.swapTwoDays())
            elif neighbourChoice == 3:
                # good neighbour choice
                return (3, self.swapSpecialistTwoNeighbourPeriods())
            elif neighbourChoice == 4:
                # Does not generates good neighbours
                return (4, self.swapTwoClosePeriodsPairs())
            elif neighbourChoice == 5:
                # supposed to be less good than 2 neighbours
                return (5, self.swapSpecialistTwoDiagonalNeighbourPeriods())
            elif neighbourChoice == 6:
                # Best generator yet
                return (6, self.swapSpecialistSameDayPeriods())
            elif neighbourChoice == 7:
                # Good generator
                return (7, self.swapSpecialistPeriodsRndDaysApart())
            elif neighbourChoice == 8:
                # Not yet implemented
                return (8, self.multipleSwaps())
        elif depth == 1:
            neighbourChoice = random.choice([0, 1, 3, 4])
            if neighbourChoice == 0:
                # good neighbour choice
                return (1, self.swapSpecialistTwoPeriods())
            elif neighbourChoice == 1:
                # good neighbour choice
                return (3, self.swapSpecialistTwoNeighbourPeriods())
            elif neighbourChoice == 2:
                # supposed to be less good than 2 neighbours
                return (5, self.swapSpecialistTwoDiagonalNeighbourPeriods())
            elif neighbourChoice == 3:
                # best generator
                return (6, self.swapSpecialistSameDayPeriods())
            elif neighbourChoice == 4:
                # Good generator
                return (7, self.swapSpecialistPeriodsRndDaysApart())
            elif neighbourChoice == 5:
                # not yet implemented
                return (8, self.multipleSwaps())
        else:
            # At depth > 1, must generate period moving only moves, that are consistent with the locals' constraints
            neighbourChoice = random.choice([0, 1, 4, 5])
            if neighbourChoice == 0:
                # good neighbour choice
                return (1, self.swapSpecialistTwoPeriods())
            elif neighbourChoice == 1:
                # excellent neighbour choice, great for optimizing at start and also after a while
                # Generates very close neighbours, local optimization.
                return (3, self.swapSpecialistTwoNeighbourPeriods())
            elif neighbourChoice == 2:
                # supposed to be bad, let's compare
                return (4, self.swapTwoClosePeriodsPairs())
            elif neighbourChoice == 3:
                # supposed to be less good than 2 neighbours
                return (5, self.swapSpecialistTwoDiagonalNeighbourPeriods())
            elif neighbourChoice == 4:
                # Dan Special!
                return (6, self.swapSpecialistSameDayPeriods())
            elif neighbourChoice == 5:
                # Good generator
                return (7, self.swapSpecialistPeriodsRndDaysApart())
            elif neighbourChoice == 6:
                # not yet implemented
                return (8, self.multipleSwaps())


    def addOrRemoveGroupMeetingWithSpecialist(self):
        groupsNeeds = self.classesAndResources.groupsNeeds != 0
        whereNeeds = np.where(groupsNeeds)
        triggeredNeed = random.randrange(0, len(whereNeeds[0]))

        triggeredGroup = whereNeeds[0][triggeredNeed]
        triggeredSpecialist = whereNeeds[1][triggeredNeed]

        triggeredLocal = random.choice(self.classesAndResources.localListBySpecialistAndGroup[triggeredGroup][triggeredSpecialist])

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

        return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def swapSpecialistTwoPeriods(self):
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

        possibleSecondPeriodsNotTeachingGroup = np.where(
            np.sum(self.meetByPeriodByDayByLocalBySubjectByGroup[:, specialistWithSwappedGroup], axis=(0, 1)) == 0)
        possibleSecondPeriodsTeachingOtherGroups = np.where(
            np.concatenate([self.meetByPeriodByDayByLocalBySubjectByGroup[:groupWithSwappedSpecialist,
                            specialistWithSwappedGroup,
                            firstLocal],
                            self.meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist + 1:,
                            specialistWithSwappedGroup,
                            firstLocal]]))
        if len(possibleSecondPeriodsNotTeachingGroup[0]) + len(possibleSecondPeriodsTeachingOtherGroups[0]) == 0:
            return None

        secondPeriodSwap = random.randrange(0, len(possibleSecondPeriodsNotTeachingGroup[0]) +
                                            len(possibleSecondPeriodsTeachingOtherGroups[0]))

        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)

        if secondPeriodSwap < len(possibleSecondPeriodsNotTeachingGroup[0]):

            secondDay = possibleSecondPeriodsNotTeachingGroup[0][secondPeriodSwap]
            secondPeriod = possibleSecondPeriodsNotTeachingGroup[1][secondPeriodSwap]

            meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist,
                                                     specialistWithSwappedGroup,
                                                     firstLocal,
                                                     firstDay,
                                                     firstPeriod] = False
            meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist,
                                                     specialistWithSwappedGroup,
                                                     firstLocal,
                                                     secondDay,
                                                     secondPeriod] = True

            return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)
        else:
            secondPeriodSwap -= len(possibleSecondPeriodsNotTeachingGroup[0])

            secondGroup = possibleSecondPeriodsTeachingOtherGroups[0][secondPeriodSwap]

            # Need to recalibrate extracted group
            if secondGroup >= groupWithSwappedSpecialist:
                secondGroup += 1

            secondDay = possibleSecondPeriodsTeachingOtherGroups[1][secondPeriodSwap]
            secondPeriod = possibleSecondPeriodsTeachingOtherGroups[2][secondPeriodSwap]

            meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal, firstDay, firstPeriod] = False
            meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal, secondDay, secondPeriod] = True

            meetByPeriodByDayByLocalBySubjectByGroup[secondGroup, specialistWithSwappedGroup, firstLocal, firstDay, firstPeriod] = True
            meetByPeriodByDayByLocalBySubjectByGroup[secondGroup, specialistWithSwappedGroup, firstLocal, secondDay, secondPeriod] = False

            return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def swapTwoDays(self):
        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
        firstDay = random.randrange(0, meetByPeriodByDayByLocalBySubjectByGroup.shape[3])
        secondDay = random.randrange(0, meetByPeriodByDayByLocalBySubjectByGroup.shape[3] - 1)
        if secondDay >= firstDay:
            secondDay += 1
        meetByPeriodByDayByLocalBySubjectByGroup[...,[firstDay, secondDay],:] = meetByPeriodByDayByLocalBySubjectByGroup[...,[secondDay, firstDay],:]
        return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def swapSpecialistTwoNeighbourPeriods(self):
        groupWithSwappedSpecialist = random.randrange(0, self.meetByPeriodByDayByLocalBySubjectByGroup.shape[0])
        groupSpecialists = np.where(np.sum(self.meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist], axis=(1, 2, 3)) > 0)[0]

        if len(groupSpecialists) == 0:
            return None

        specialistWithSwappedGroup = random.choice(groupSpecialists)

        possibleFirstPeriods = np.where(self.meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist, specialistWithSwappedGroup])
        firstPeriodSwap = random.randrange(0, len(possibleFirstPeriods[0]))
        firstLocal = possibleFirstPeriods[0][firstPeriodSwap]
        firstDay = possibleFirstPeriods[1][firstPeriodSwap]
        firstPeriod = possibleFirstPeriods[2][firstPeriodSwap]

        minusFirstPeriod = (firstPeriod + self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4] - 1) % self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4]
        plusFirstPeriod = (firstPeriod + 1) % self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4]
        minusFirstDay = (firstDay + self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3] - 1) % self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3]
        plusFirstDay = (firstDay + 1) % self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3]
        
        possibleSecondDays = [minusFirstDay, firstDay, firstDay, plusFirstDay]
        possibleSecondPeriods = [firstPeriod, minusFirstPeriod, plusFirstPeriod, firstPeriod]
        possibleSecondPeriodsNotTeachingGroup = np.where((np.sum(self.meetByPeriodByDayByLocalBySubjectByGroup[:, specialistWithSwappedGroup], axis=(0, 1)) == 0)[possibleSecondDays, possibleSecondPeriods])[0]
        possibleSecondPeriodsTeachingOtherGroups = np.where(np.concatenate([self.meetByPeriodByDayByLocalBySubjectByGroup[:groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal], self.meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist + 1:, specialistWithSwappedGroup, firstLocal]])[:, possibleSecondDays, possibleSecondPeriods])
        if len(possibleSecondPeriodsNotTeachingGroup) + len(possibleSecondPeriodsTeachingOtherGroups[0]) == 0:
            return None

        secondPeriodSwap = random.randrange(0, len(possibleSecondPeriodsNotTeachingGroup) + len(possibleSecondPeriodsTeachingOtherGroups[0]))

        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)

        if secondPeriodSwap < len(possibleSecondPeriodsNotTeachingGroup):
            selectedIndex  = possibleSecondPeriodsNotTeachingGroup[secondPeriodSwap]
            secondDay = possibleSecondDays[selectedIndex]
            secondPeriod = possibleSecondPeriods[selectedIndex]

            meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal, firstDay, firstPeriod] = False
            meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal, secondDay, secondPeriod] = True

            return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)
        else:
            secondPeriodSwap -= len(possibleSecondPeriodsNotTeachingGroup)

            selectedIndex = possibleSecondPeriodsTeachingOtherGroups[1][secondPeriodSwap]
            secondGroup = possibleSecondPeriodsTeachingOtherGroups[0][secondPeriodSwap]
            secondDay = possibleSecondDays[selectedIndex]
            secondPeriod = possibleSecondPeriods[selectedIndex]

            # Need to recalibrate extracted group
            if secondGroup >= groupWithSwappedSpecialist:
                secondGroup += 1

            meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal, firstDay, firstPeriod] = False
            meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal, secondDay, secondPeriod] = True

            meetByPeriodByDayByLocalBySubjectByGroup[secondGroup, specialistWithSwappedGroup, firstLocal, firstDay, firstPeriod] = True
            meetByPeriodByDayByLocalBySubjectByGroup[secondGroup, specialistWithSwappedGroup, firstLocal, secondDay, secondPeriod] = False

            return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def swapSpecialistPeriodsRndDaysApart(self):
        groupWithSwappedSpecialist = random.randrange(0, self.meetByPeriodByDayByLocalBySubjectByGroup.shape[0])
        groupSpecialists = \
        np.where(np.sum(self.meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist], axis=(1, 2, 3)) > 0)[
            0]

        if len(groupSpecialists) == 0:
            return None

        specialistWithSwappedGroup = random.choice(groupSpecialists)

        possibleFirstPeriods = np.where(
            self.meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist, specialistWithSwappedGroup])
        firstPeriodSwap = random.randrange(0, len(possibleFirstPeriods[0]))
        firstLocal = possibleFirstPeriods[0][firstPeriodSwap]
        firstDay = possibleFirstPeriods[1][firstPeriodSwap]
        firstPeriod = possibleFirstPeriods[2][firstPeriodSwap]

        randomSwitch = random.choice([1, 2, 3, 4, 5])

        minusRandomDay = (firstDay + self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3] - randomSwitch) % \
                        self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3]
        plusRandomDay = (firstDay + randomSwitch) % self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3]
        minusFirstPeriod = (firstPeriod + self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4] - 1) % self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4]
        plusFirstPeriod = (firstPeriod + 1) % self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4]

        possibleSecondDays = [minusRandomDay, plusRandomDay, minusRandomDay, plusRandomDay]
        possibleSecondPeriods = [minusFirstPeriod, minusFirstPeriod, plusFirstPeriod, plusFirstPeriod]
        possibleSecondPeriodsNotTeachingGroup = np.where(
            (np.sum(self.meetByPeriodByDayByLocalBySubjectByGroup[:, specialistWithSwappedGroup], axis=(0, 1)) == 0)[
                possibleSecondDays, possibleSecondPeriods])[0]
        possibleSecondPeriodsTeachingOtherGroups = np.where(np.concatenate([
                                                                               self.meetByPeriodByDayByLocalBySubjectByGroup[
                                                                               :groupWithSwappedSpecialist,
                                                                               specialistWithSwappedGroup, firstLocal],
                                                                               self.meetByPeriodByDayByLocalBySubjectByGroup[
                                                                               groupWithSwappedSpecialist + 1:,
                                                                               specialistWithSwappedGroup,
                                                                               firstLocal]])[:, possibleSecondDays,
                                                            possibleSecondPeriods])
        if len(possibleSecondPeriodsNotTeachingGroup) + len(possibleSecondPeriodsTeachingOtherGroups[0]) == 0:
            return None

        secondPeriodSwap = random.randrange(0, len(possibleSecondPeriodsNotTeachingGroup) + len(
            possibleSecondPeriodsTeachingOtherGroups[0]))

        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)

        if secondPeriodSwap < len(possibleSecondPeriodsNotTeachingGroup):
            selectedIndex = possibleSecondPeriodsNotTeachingGroup[secondPeriodSwap]
            secondDay = possibleSecondDays[selectedIndex]
            secondPeriod = possibleSecondPeriods[selectedIndex]

            meetByPeriodByDayByLocalBySubjectByGroup[
                groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal, firstDay, firstPeriod] = False
            meetByPeriodByDayByLocalBySubjectByGroup[
                groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal, secondDay, secondPeriod] = True

            return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)
        else:
            secondPeriodSwap -= len(possibleSecondPeriodsNotTeachingGroup)

            selectedIndex = possibleSecondPeriodsTeachingOtherGroups[1][secondPeriodSwap]
            secondGroup = possibleSecondPeriodsTeachingOtherGroups[0][secondPeriodSwap]
            secondDay = possibleSecondDays[selectedIndex]
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

            return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def swapSpecialistSameDayPeriods(self):
        groupWithSwappedSpecialist = random.randrange(0, self.meetByPeriodByDayByLocalBySubjectByGroup.shape[0])
        groupSpecialists = \
        np.where(np.sum(self.meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist], axis=(1, 2, 3)) > 0)[
            0]

        if len(groupSpecialists) == 0:
            return None

        specialistWithSwappedGroup = random.choice(groupSpecialists)

        possibleFirstPeriods = np.where(
            self.meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist, specialistWithSwappedGroup])
        firstPeriodSwap = random.randrange(0, len(possibleFirstPeriods[0]))
        firstLocal = possibleFirstPeriods[0][firstPeriodSwap]
        firstDay = possibleFirstPeriods[1][firstPeriodSwap]
        firstPeriod = possibleFirstPeriods[2][firstPeriodSwap]

        possibleSecondPeriods = (np.arange(0, self.classesAndResources.school.periodsInDay - 1) + firstPeriod) % self.classesAndResources.school.periodsInDay

        possibleSecondPeriodsNotTeachingGroup = np.where((np.sum(self.meetByPeriodByDayBySpecialistByGroup[:, specialistWithSwappedGroup, firstDay], axis=0) == 0)[possibleSecondPeriods])[0]
        possibleSecondPeriodsTeachingOtherGroups = np.where(np.concatenate([
                                                                               self.meetByPeriodByDayByLocalBySubjectByGroup[
                                                                               :groupWithSwappedSpecialist,
                                                                               specialistWithSwappedGroup, firstLocal, firstDay],
                                                                               self.meetByPeriodByDayByLocalBySubjectByGroup[
                                                                               groupWithSwappedSpecialist + 1:,
                                                                               specialistWithSwappedGroup,
                                                                               firstLocal, firstDay]])[:, possibleSecondPeriods])

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

            return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)
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

            return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def swapSpecialistTwoDiagonalNeighbourPeriods(self):
        groupWithSwappedSpecialist = random.randrange(0, self.meetByPeriodByDayByLocalBySubjectByGroup.shape[0])
        groupSpecialists = \
        np.where(np.sum(self.meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist], axis=(1, 2, 3)) > 0)[
            0]

        if len(groupSpecialists) == 0:
            return None

        specialistWithSwappedGroup = random.choice(groupSpecialists)

        possibleFirstPeriods = np.where(
            self.meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist, specialistWithSwappedGroup])
        firstPeriodSwap = random.randrange(0, len(possibleFirstPeriods[0]))
        firstLocal = possibleFirstPeriods[0][firstPeriodSwap]
        firstDay = possibleFirstPeriods[1][firstPeriodSwap]
        firstPeriod = possibleFirstPeriods[2][firstPeriodSwap]

        minusFirstPeriod = (firstPeriod + self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4] - 1) % \
                           self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4]
        plusFirstPeriod = (firstPeriod + 1) % self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4]
        minusFirstDay = (firstDay + self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3] - 1) % \
                        self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3]
        plusFirstDay = (firstDay + 1) % self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3]

        possibleSecondDays = [minusFirstDay, plusFirstDay, minusFirstDay, plusFirstDay]
        possibleSecondPeriods = [minusFirstPeriod, minusFirstPeriod, plusFirstPeriod, plusFirstPeriod]
        possibleSecondPeriodsNotTeachingGroup = np.where(
            (np.sum(self.meetByPeriodByDayByLocalBySubjectByGroup[:, specialistWithSwappedGroup], axis=(0, 1)) == 0)[
                possibleSecondDays, possibleSecondPeriods])[0]
        possibleSecondPeriodsTeachingOtherGroups = np.where(
            np.concatenate([self.meetByPeriodByDayByLocalBySubjectByGroup[:groupWithSwappedSpecialist,
                            specialistWithSwappedGroup,
                            firstLocal],
                            self.meetByPeriodByDayByLocalBySubjectByGroup[groupWithSwappedSpecialist + 1:,
                            specialistWithSwappedGroup,
                            firstLocal]])[:, possibleSecondDays,possibleSecondPeriods])
        if len(possibleSecondPeriodsNotTeachingGroup) + len(possibleSecondPeriodsTeachingOtherGroups[0]) == 0:
            return None

        secondPeriodSwap = random.randrange(0, len(possibleSecondPeriodsNotTeachingGroup) + len(
            possibleSecondPeriodsTeachingOtherGroups[0]))

        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)

        if secondPeriodSwap < len(possibleSecondPeriodsNotTeachingGroup):
            selectedIndex = possibleSecondPeriodsNotTeachingGroup[secondPeriodSwap]
            secondDay = possibleSecondDays[selectedIndex]
            secondPeriod = possibleSecondPeriods[selectedIndex]

            meetByPeriodByDayByLocalBySubjectByGroup[
                groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal, firstDay, firstPeriod] = False
            meetByPeriodByDayByLocalBySubjectByGroup[
                groupWithSwappedSpecialist, specialistWithSwappedGroup, firstLocal, secondDay, secondPeriod] = True

            return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)
        else:
            secondPeriodSwap -= len(possibleSecondPeriodsNotTeachingGroup)

            selectedIndex = possibleSecondPeriodsTeachingOtherGroups[1][secondPeriodSwap]
            secondGroup = possibleSecondPeriodsTeachingOtherGroups[0][secondPeriodSwap]
            secondDay = possibleSecondDays[selectedIndex]
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

            return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def multipleSwaps(self):
        first = self.swapSpecialistSameDayPeriods()
#        second = first.swapSpecialistTwoPeriods()
#        final = second.swapSpecialistTwoPeriods()
        return first

    def swapTwoClosePeriodsPairs(self): # Turned out not to be a good neighbour generator
        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
        firstDay = random.randrange(0, meetByPeriodByDayByLocalBySubjectByGroup.shape[3])
        secondDay = random.randrange(0, meetByPeriodByDayByLocalBySubjectByGroup.shape[3])
        firstPeriod = random.choice(list(range(self.classesAndResources.school.periodsInAm - 1)) + list(map(lambda pmPeriod: self.classesAndResources.school.periodsInAm + pmPeriod, range(self.classesAndResources.school.periodsInPm - 1))))

        secondPeriodAmChoice = list(range(self.classesAndResources.school.periodsInAm - 1))
        secondPeriodPmChoice = list(map(lambda pmPeriod: self.classesAndResources.school.periodsInAm + pmPeriod, range(self.classesAndResources.school.periodsInPm - 1)))

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
        
        meetByPeriodByDayByLocalBySubjectByGroup[...,[firstDay, firstDay, secondDay, secondDay],[firstPeriod, firstPeriod + 1, secondPeriod, secondPeriod + 1]] = meetByPeriodByDayByLocalBySubjectByGroup[...,[secondDay, secondDay, firstDay, firstDay],[secondPeriod, secondPeriod + 1, firstPeriod, firstPeriod + 1]]
        return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def toString(self):
        argsWhere = np.where(self.meetByPeriodByDayByLocalBySubjectByGroup)
        groupByPeriodByDayBySpecialist = np.zeros((self.meetByPeriodByDayByLocalBySubjectByGroup.shape[1], self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3], self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4]))
        vfunc = lambda x: (floor(self.classesAndResources.groups[x].level)) + ((x + 1) / 100)
        get_group_level_with_id = np.vectorize(vfunc)
        groupByPeriodByDayBySpecialist[argsWhere[1], argsWhere[3], argsWhere[4]] = get_group_level_with_id(argsWhere[0])

        specialistByPeriodByDayByGroup = np.zeros((self.meetByPeriodByDayByLocalBySubjectByGroup.shape[0], self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3], self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4]))
        specialistByPeriodByDayByGroup[argsWhere[0], argsWhere[3], argsWhere[4]] = argsWhere[1] + 1

        return self.classesAndResources.toString() + """

Groups schedules (0 = no specialist):
""" + "\n".join(map(lambda indexAndX: self.classesAndResources.groups[indexAndX[0]].name + ":\n" + str(indexAndX[1].T), enumerate(specialistByPeriodByDayByGroup))) + """

Specialists schedules (0 = no group):
""" + "\n".join(map(lambda indexAndX: self.classesAndResources.specialists[indexAndX[0]].name + ":\n" + str(indexAndX[1].T), enumerate(groupByPeriodByDayBySpecialist))) + """

Solution cost: """ + str(self.getTotalCost().toString())