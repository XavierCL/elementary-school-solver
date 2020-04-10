from solver.classesAndResources import ClassesAndResources
from solver.specialist import Specialist
from solver.group import Group
from solver.local import Local
from problemInstances import school2
import numpy as np

def getHalfTimeTutorHardCost(solutionInstance):
    # Penalizes every time an AM where an absent tutor does not have two periods without specialist
    # Penalizes every time a PM where an absent tutor does not have two periods without specialist

    cost = 0

    fullDayNonFreeTutors = np.sum(solutionInstance.classesAndResources.tutorFreePeriods, axis=2) == 0
    amNonFreeTutors = np.logical_and(np.sum(solutionInstance.classesAndResources.tutorFreePeriods[..., :solutionInstance.classesAndResources.school.periodsInAm], axis=2) == 0, ~fullDayNonFreeTutors)
    pmNonFreeTutors = np.logical_and(np.sum(solutionInstance.classesAndResources.tutorFreePeriods[..., solutionInstance.classesAndResources.school.periodsInAm:], axis=2) == 0, ~fullDayNonFreeTutors)

    meetByPeriodByDayByGroup = np.sum(solutionInstance.meetByPeriodByDayBySpecialistByGroup, axis=1)

    # Full day absent tutor must have 1 speciality
    cost += np.sum((np.sum(meetByPeriodByDayByGroup, axis=2)[fullDayNonFreeTutors] - 1)**2)

    # AM day absent tutor must have 1 speciality
    cost += np.sum((np.sum(meetByPeriodByDayByGroup[..., :solutionInstance.classesAndResources.school.periodsInAm], axis=2)[amNonFreeTutors] - 1)**2)

    # PM day absent tutor must have 0 speciality
    cost += np.sum((np.sum(meetByPeriodByDayByGroup[..., solutionInstance.classesAndResources.school.periodsInAm:], axis=2)[pmNonFreeTutors] - 1)**2)

    return cost

def classes2():

    school = school2.school2Instance()

    def all_period_available():
        return np.ones((school.daysInCycle, school.periodsInDay)).astype(np.bool)

    groups = [
        Group(0, "First Some group", 0, np.asarray([1, 0]), all_period_available()),
        Group(1, "Second Some group", 1, np.asarray([0, 1]), all_period_available()),
    ]

    specialists = [
        Specialist(0, "1 (Alizés gr09 et moins)", all_period_available()),
        Specialist(1, "2 (Mousserons + gr3.1)", all_period_available())
    ]

    locals = [
        Local(0, "First premise english room (Alizés)", 0, {0}, {0}),
        Local(1, "Second premise english room (Mousserons)", 1, {1}, {1})
    ]

    return ClassesAndResources(school, groups, specialists, locals, {1: getHalfTimeTutorHardCost})