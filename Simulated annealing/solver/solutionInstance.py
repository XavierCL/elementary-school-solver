from solver.solutionCost import SolutionCost
from solver.classesAndResources import ClassesAndResources

import numpy as np

class SolutionInstance:

    def __init__(self, classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup):
        self.classesAndResources: ClassesAndResources = classesAndResources
        self.meetByPeriodByDayByLocalBySubjectByGroup = meetByPeriodByDayByLocalBySubjectByGroup
        self.meetByPeriodByDayBySpecialistByGroup = np.sum(self.meetByPeriodByDayByLocalBySubjectByGroup, axis=2) != 0

    def equals(self, otherSolutionInstance):
        return np.array_equal(self.meetByPeriodByDayByLocalBySubjectByGroup, otherSolutionInstance.meetByPeriodByDayByLocalBySubjectByGroup)

    def assignGroupToSpecialistDayAndPeriod(self, specialist, day, period, local, oldGroupId, newGroupId):
        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
        meetByPeriodByDayByLocalBySubjectByGroup[[oldGroupId, newGroupId], specialist, local, day, period] = \
            meetByPeriodByDayByLocalBySubjectByGroup[[newGroupId, oldGroupId], specialist, local, day, period]
        
        return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def assignLocalToSpecialistDayAndPeriod(self, specialist, day, period, group, oldLocalId, newLocalId):
        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
        meetByPeriodByDayByLocalBySubjectByGroup[group, specialist, [oldLocalId, newLocalId], day, period] = \
            meetByPeriodByDayByLocalBySubjectByGroup[group, specialist, [newLocalId, oldLocalId], day, period]
        
        return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def removeSpecialistDayPeriodMeeting(self, specialist, day, period):
        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
        meetByPeriodByDayByLocalBySubjectByGroup[:, specialist, :, day, period] = False
        
        return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def addSpecialistDayPeriodMeetingWithGroupAtLocal(self, specialist, day, period, group, local):
        meetByPeriodByDayByLocalBySubjectByGroup = np.copy(self.meetByPeriodByDayByLocalBySubjectByGroup)
        meetByPeriodByDayByLocalBySubjectByGroup[group, specialist, local, day, period] = True
        
        return SolutionInstance(self.classesAndResources, meetByPeriodByDayByLocalBySubjectByGroup)

    def getTotalCost(self) -> SolutionCost:
        hardConstraintViolationCount = self.getHardConstraintCost()
        customHardCost = self.classesAndResources.getDepthCost(self, 0)

        meetArgs = np.where(self.meetByPeriodByDayByLocalBySubjectByGroup)

        premiseConstraintViolationCount = self.getPremiseConstraintCost(meetArgs)
        customPremiseCost = self.classesAndResources.getDepthCost(self, 1)

        (softiesConstraintViolationCount, softiesDetails) = self.getSoftConstraintCost(meetArgs)
        customSoftCost = self.classesAndResources.getDepthCost(self, 2)

        return SolutionCost(np.asarray([hardConstraintViolationCount + customHardCost,
                                        premiseConstraintViolationCount + customPremiseCost,
                                        softiesConstraintViolationCount + customSoftCost]),
                            softiesDetails)

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
        return np.sum(np.abs(np.sum(self.meetByPeriodByDayBySpecialistByGroup, axis=(2, 3)) -
                             self.classesAndResources.groupsNeeds))

    def singleSpecialistByGroupPeriodViolationCost(self):
        # No groups see a specialist twice at the same period
        violations = np.sum(self.meetByPeriodByDayBySpecialistByGroup, axis=1) - 1
        return np.sum(violations[violations > 0])

    def singleGroupByFreeSpecialistPeriodViolationCost(self):
        # No specialists see more than a group when they are free
        specialistMeetDiffWithFreePeriods = np.sum(self.meetByPeriodByDayBySpecialistByGroup, axis=0) - \
                                            self.classesAndResources.specialistsFreePeriods
        return np.sum(specialistMeetDiffWithFreePeriods[specialistMeetDiffWithFreePeriods > 0])

    def singleLocalOccupancyViolationCost(self):
        # No local see people twice at the same period
        violations = np.sum(self.meetByPeriodByDayByLocalBySubjectByGroup, axis=(0, 1)) - 1
        return np.sum(violations[violations > 0])

    def getPremiseConstraintCost(self, meetArgs):

        premiseConstraintViolationCount = 0

        # Two different premises cannot be one period after the other (except at noon)
        meetByPeriodByDayByPremiseBySpecialist = np.zeros((self.meetByPeriodByDayByLocalBySubjectByGroup.shape[1],
                                                           self.classesAndResources.premiseCount,
                                                           self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3],
                                                           self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4])
                                                          ).astype(np.bool)
        meetByPeriodByDayByPremiseBySpecialist[meetArgs[1],
                                               self.classesAndResources.premiseByLocal[meetArgs[2]],
                                               meetArgs[3],
                                               meetArgs[4]] = True
        for firstClosePeriod in range(self.classesAndResources.school.periodsInAm - 1):
            premiseConstraintViolationCount += np.sum(np.sum(np.sum(
                meetByPeriodByDayByPremiseBySpecialist[...,firstClosePeriod:firstClosePeriod+2], axis=3) >= 1, axis=1) > 1)
        for firstClosePeriod in range(self.classesAndResources.school.periodsInPm - 1):
            firstClosePeriod += self.classesAndResources.school.periodsInAm
            premiseConstraintViolationCount += np.sum(np.sum(np.sum(
                meetByPeriodByDayByPremiseBySpecialist[...,firstClosePeriod:firstClosePeriod+2], axis=3) >= 1, axis=1) > 1)

        return premiseConstraintViolationCount

    def getSoftConstraintCost(self, meetArgs):
        spreadBreaks = 15
        spreadSpecialties = 10
        tutorFreePeriodsAcrossTheDaysCost = self.getTutorFreePeriodsAcrossDaysCost() * spreadBreaks
        tutorFreePeriodsAcrossThePeriodsCost = self.getTutorFreePeriodsAcrossPeriodsCost() * spreadBreaks * 15
#        tutorFreePeriodsAcrossTheBoard = self.getTutorFreePeriodsAcrossTheBoardCost() * 0
        groupsSubjectPeriodsAcrossTheDaysCost = self.getGroupsSubjectsAcrossTheDaysCost() * spreadSpecialties * 1.5
        groupsSubjectPeriodsAcrossThePeriodsCost = self.getGroupsSubjectsAcrossThePeriodsCost() * spreadSpecialties
#        groupsSubjectPeriodsAcrossTheBoardCost = self.getGroupsSubjectsAcrossTheBoardCost() * 0
        teachSameLevelsTogetherCost = self.getTeachSameLevelsTogetherCost(meetArgs) * 40

        return ((tutorFreePeriodsAcrossTheDaysCost +
                 tutorFreePeriodsAcrossThePeriodsCost +
#                 tutorFreePeriodsAcrossTheBoard +
                 groupsSubjectPeriodsAcrossTheDaysCost +
                 groupsSubjectPeriodsAcrossThePeriodsCost +
#                 groupsSubjectPeriodsAcrossTheBoardCost +
                 teachSameLevelsTogetherCost
                 ) / 24_000_000,
                [tutorFreePeriodsAcrossTheDaysCost,
                 tutorFreePeriodsAcrossThePeriodsCost,
                 0,
                 groupsSubjectPeriodsAcrossTheDaysCost,
                 groupsSubjectPeriodsAcrossThePeriodsCost,
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
        shiftedDaysByGroup[groupsWhereStarts] = shiftedDaysByGroup[shiftedGroupsWhereStarts] - \
                                                self.classesAndResources.school.daysInCycle
        dayDistances = np.sum((self.classesAndResources.school.daysInCycle - (daysByGroup - shiftedDaysByGroup)).astype(np.float64)**4)
        cumulativeDays = np.sum(np.sum(meetByPeriodByDayByGroup, axis=2)**4)
        return dayDistances + cumulativeDays

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
        shiftedPeriodsByGroup[groupsWhereStarts] = shiftedPeriodsByGroup[shiftedGroupsWhereStarts] - \
                                                   self.classesAndResources.school.periodsInDay
        periodDistances = np.sum((self.classesAndResources.school.periodsInDay - (periodsByGroup - shiftedPeriodsByGroup)).astype(np.float64)**3)
        cumulativePeriods = np.sum(np.sum(meetByDayByPeriodByGroup, axis=2)**3)
        return periodDistances + cumulativePeriods

    def getTutorFreePeriodsAcrossTheBoardCost(self):
        # Disperse a tutor free periods across the board
        meetByDayAndPeriodByGroup = np.sum(self.meetByPeriodByDayBySpecialistByGroup, axis=1).reshape(
            self.meetByPeriodByDayBySpecialistByGroup.shape[0], -1)
        meetArgsByDayAndPeriodByGroup = np.where(meetByDayAndPeriodByGroup)
        daysAndPeriodsByGroup = meetArgsByDayAndPeriodByGroup[1]
        shiftedDaysAndPeriodsByGroup = np.roll(daysAndPeriodsByGroup, 1)
        groups = meetArgsByDayAndPeriodByGroup[0]
        shiftedGroups = np.roll(groups, 1)
        groupsStarts = groups != shiftedGroups
        groupsWhereStarts = np.where(groupsStarts)[0]
        shiftedGroupsWhereStarts = np.roll(groupsWhereStarts, -1)
        shiftedDaysAndPeriodsByGroup[groupsWhereStarts] = shiftedDaysAndPeriodsByGroup[shiftedGroupsWhereStarts] - \
                                                          (self.classesAndResources.school.periodsInDay *
                                                           self.classesAndResources.school.daysInCycle)
        return np.sum((self.classesAndResources.school.daysInCycle * self.classesAndResources.school.periodsInDay - (daysAndPeriodsByGroup - shiftedDaysAndPeriodsByGroup)).astype(np.float64)**3)

    def getGroupsSubjectsAcrossTheDaysCost(self):
        # Disperse a group's single subject across the days
        meetByPeriodByDayBySpecialistAndGroup = self.meetByPeriodByDayBySpecialistByGroup.reshape(
            (-1,
             self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3],
             self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4]))
        meetArgsByPeriodByDayBySpecialistAndGroup = np.where(meetByPeriodByDayBySpecialistAndGroup)
        daysBySpecialistAndGroup = meetArgsByPeriodByDayBySpecialistAndGroup[1]
        shiftedDaysBySpecialistAndGroup = np.roll(daysBySpecialistAndGroup, 1)
        specialistsAndGroups = meetArgsByPeriodByDayBySpecialistAndGroup[0]
        shiftedSpecialistsAndGroups = np.roll(specialistsAndGroups, 1)
        specialistsAndGroupsStarts = specialistsAndGroups != shiftedSpecialistsAndGroups
        specialistsAndGroupsWhereStarts = np.where(specialistsAndGroupsStarts)[0]
        shiftedSpecialistsAndGroupsWhereStarts = np.roll(specialistsAndGroupsWhereStarts, -1)
        shiftedDaysBySpecialistAndGroup[specialistsAndGroupsWhereStarts] = \
            shiftedDaysBySpecialistAndGroup[shiftedSpecialistsAndGroupsWhereStarts] - \
            self.classesAndResources.school.daysInCycle
        dayDistances = np.sum((self.classesAndResources.school.daysInCycle - (daysBySpecialistAndGroup - shiftedDaysBySpecialistAndGroup)).astype(np.float64)**4)
        cumulativeDays = np.sum(np.sum(meetByPeriodByDayBySpecialistAndGroup, axis=2)**4)
        return dayDistances + cumulativeDays

    def getGroupsSubjectsAcrossThePeriodsCost(self):
        # Disperse a group's single subject across the periods
        meetByDayByPeriodBySpecialistAndGroup = np.swapaxes(self.meetByPeriodByDayBySpecialistByGroup, 2, 3).reshape(
            (-1,
             self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4],
             self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3]))
        meetArgsByDayByPeriodBySpecialistAndGroup = np.where(meetByDayByPeriodBySpecialistAndGroup)
        periodsBySpecialistAndGroup = meetArgsByDayByPeriodBySpecialistAndGroup[1]
        shiftedPeriodsBySpecialistAndGroup = np.roll(periodsBySpecialistAndGroup, 1)
        specialistsAndGroups = meetArgsByDayByPeriodBySpecialistAndGroup[0]
        shiftedSpecialistsAndGroups = np.roll(specialistsAndGroups, 1)
        specialistsAndGroupsStarts = specialistsAndGroups != shiftedSpecialistsAndGroups
        specialistsAndGroupsWhereStarts = np.where(specialistsAndGroupsStarts)[0]
        shiftedSpecialistsAndGroupsWhereStarts = np.roll(specialistsAndGroupsWhereStarts, -1)
        shiftedPeriodsBySpecialistAndGroup[specialistsAndGroupsWhereStarts] = \
            shiftedPeriodsBySpecialistAndGroup[shiftedSpecialistsAndGroupsWhereStarts] - \
            self.classesAndResources.school.periodsInDay
        periodDistances = np.sum((self.classesAndResources.school.periodsInDay - (periodsBySpecialistAndGroup - shiftedPeriodsBySpecialistAndGroup)).astype(np.float64)**3)
        cumulativePeriods = np.sum(np.sum(meetByDayByPeriodBySpecialistAndGroup, axis=2)**2)
        return periodDistances + cumulativePeriods

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
        return np.sum((self.classesAndResources.school.daysInCycle * self.classesAndResources.school.periodsInDay - (daysAndPeriodsBySpecialistAndGroup -
                       shiftedDaysAndPeriodsBySpecialistAndGroup)).astype(np.float64)**3)

    def getTeachSameLevelsTogetherCost(self, meetArgs):
        # Group together same years for specialists
        groupTogetherSameYearCost = 0.
        levelByPeriodByDayBySpecialist = np.ones((self.meetByPeriodByDayByLocalBySubjectByGroup.shape[1],
                                                  self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3],
                                                  self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4])) * \
                                         (self.classesAndResources.maxLevel + 1)
        levelByPeriodByDayBySpecialist[meetArgs[1], meetArgs[3], meetArgs[4]] = \
            self.classesAndResources.levelByGroup[meetArgs[0]]

        groupByPeriodByDayBySpecialist = np.ones((self.meetByPeriodByDayByLocalBySubjectByGroup.shape[1],
                                                  self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3],
                                                  self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4])) * \
                                         (len(self.classesAndResources.groups) + 1)
        groupByPeriodByDayBySpecialist[meetArgs[1], meetArgs[3], meetArgs[4]] = meetArgs[0]

        for firstClosePeriod in range(self.classesAndResources.school.periodsInDay - 1):
            groupTogetherSameYearCost += np.sum(np.logical_or(levelByPeriodByDayBySpecialist[..., firstClosePeriod] !=
                                                              levelByPeriodByDayBySpecialist[..., firstClosePeriod + 1],
                                                              np.logical_and(groupByPeriodByDayBySpecialist[
                                                                                 ..., firstClosePeriod] ==
                                                                             groupByPeriodByDayBySpecialist[
                                                                                 ..., firstClosePeriod + 1],
                                                                             groupByPeriodByDayBySpecialist[
                                                                                 ..., firstClosePeriod] != len(
                                                                                 self.classesAndResources.groups) + 1)))
        return groupTogetherSameYearCost ** 2

    def toString(self):
        argsWhere = np.where(self.meetByPeriodByDayByLocalBySubjectByGroup)
        groupByPeriodByDayBySpecialist = np.zeros((self.meetByPeriodByDayByLocalBySubjectByGroup.shape[1],
                                                   self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3],
                                                   self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4]))
        groupByPeriodByDayBySpecialist[argsWhere[1], argsWhere[3], argsWhere[4]] = np.floor(self.classesAndResources.levelByGroup[argsWhere[0]]) + (argsWhere[0] + 1) / 100.0

        specialistByPeriodByDayByGroup = np.zeros((self.meetByPeriodByDayByLocalBySubjectByGroup.shape[0],
                                                   self.meetByPeriodByDayByLocalBySubjectByGroup.shape[3],
                                                   self.meetByPeriodByDayByLocalBySubjectByGroup.shape[4]))
        specialistByPeriodByDayByGroup[argsWhere[0], argsWhere[3], argsWhere[4]] = argsWhere[1] + 1
        
        return self.classesAndResources.toString() + """

Groups schedules (0 = no specialist):
""" + "\n".join(map(lambda indexAndX: self.classesAndResources.groups[indexAndX[0]].name +
                                      ":\n" + str(indexAndX[1].T), enumerate(specialistByPeriodByDayByGroup))) + """

Specialists schedules (0 = no group):
""" + "\n".join(map(lambda indexAndX: self.classesAndResources.specialists[indexAndX[0]].name +
                                      ":\n" + str(indexAndX[1].T), enumerate(groupByPeriodByDayBySpecialist))) + """

""" + SolutionCost.getDisplayHeader() + """
""" + str(self.getTotalCost().toString())