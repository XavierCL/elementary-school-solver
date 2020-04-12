from solver.classesAndResources import ClassesAndResources
from solver.specialist import Specialist
from solver.group import Group
from solver.local import Local
from problemInstances import school1
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

def frankClassesInstance():

    school = school1.school1Instance()

    def all_period_available():
        return np.ones((school.daysInCycle, school.periodsInDay)).astype(np.bool)

    def no_period_available():
        return np.zeros((school.daysInCycle, school.periodsInDay)).astype(np.bool)

    # Dispos (temps plein pour tous sauf CISA1 et CISA2)
    enseignantTempsPleinDispos = all_period_available()
    adaptationIsabelleDispos = all_period_available()
    adaptationIsabelleDispos[5] = False
    adaptationMariePierDispos = all_period_available()
    adaptationMariePierDispos[0] = False

    groups = [
        Group(0, "P Annabelle", 0, np.asarray([0, 0, 1, 2, 0, 0]), enseignantTempsPleinDispos),
        Group(1, "P Jo-Annie", 0, np.asarray([0, 0, 1, 2, 0, 0]), enseignantTempsPleinDispos),
        Group(2, "P Nadine", 0, np.asarray([0, 0, 1, 2, 0, 0]), enseignantTempsPleinDispos),
        
        Group(3, "1e Marie-Ève", 1, np.asarray([2, 0, 3, 4, 0, 0]), enseignantTempsPleinDispos),
        Group(4, "1e Chantal", 1, np.asarray([2, 0, 3, 4, 0, 0]), enseignantTempsPleinDispos),
        
        Group(5, "2e Valérie", 2, np.asarray([2, 0, 3, 4, 0, 0]), enseignantTempsPleinDispos),
        Group(6, "2e Josée", 2, np.asarray([2, 3, 0, 4, 0, 0]), enseignantTempsPleinDispos),

        Group(7, "3e Karyne", 3, np.asarray([2, 3, 0, 4, 0, 0]), enseignantTempsPleinDispos),
        Group(8, "3e Marie", 3, np.asarray([2, 3, 0, 4, 0, 0]), enseignantTempsPleinDispos),
        Group(9, "3e Anne", 3, np.asarray([2, 3, 0, 0, 4, 0]), enseignantTempsPleinDispos),
        
        Group(10, "4e Anne-Marie", 4, np.asarray([3, 2, 0, 4, 0, 0]), enseignantTempsPleinDispos),
        Group(11, "4e Karine", 4, np.asarray([3, 2, 0, 4, 0, 0]), enseignantTempsPleinDispos),
        
        Group(12, "5e Brigitte", 5, np.asarray([3, 2, 0, 0, 4, 0]), enseignantTempsPleinDispos),
        Group(13, "5e Jean-Yves", 5, np.asarray([3, 2, 0, 0, 4, 0]), enseignantTempsPleinDispos),
        
        Group(14, "5&6 M-Ève M.", 5.5, np.asarray([3, 2, 0, 0, 4, 0]), enseignantTempsPleinDispos),

        Group(15, "6e Annie", 6, np.asarray([0, 2, 0, 0, 4, 3]), enseignantTempsPleinDispos),
        Group(16, "6e France", 6, np.asarray([0, 2, 0, 0, 4, 3]), enseignantTempsPleinDispos),

        Group(17, "Adp Isabelle", 7, np.asarray([1, 2, 0, 0, 6, 0]), adaptationIsabelleDispos),
        Group(18, "Adp M-Pier", 7, np.asarray([1, 2, 0, 0, 6, 0]), adaptationMariePierDispos),
        Group(19, "Adp M-Ève C.", 7, np.asarray([1, 3, 0, 0, 5, 0]), enseignantTempsPleinDispos)
    ]

    englishSpecialistFreePeriods = all_period_available()
    englishSpecialistFreePeriods[[4, 9]] = False

    frankSpecialistFreePeriods = all_period_available()
    frankSpecialistFreePeriods[[1, 7]] = False
    frankSpecialistFreePeriods[4][0] = False
    frankSpecialistFreePeriods[4][1] = False
    frankSpecialistFreePeriods[4][2] = False
    frankSpecialistFreePeriods[5][3] = False
    frankSpecialistFreePeriods[5][4] = False

    otherMusicSpecialistFreePeriods = no_period_available()
    otherMusicSpecialistFreePeriods[[1, 4, 7]] = True

    scienceSpecialistFreePeriods = no_period_available()
    scienceSpecialistFreePeriods[1][3] = True
    scienceSpecialistFreePeriods[1][4] = True
    scienceSpecialistFreePeriods[4][0] = True
    scienceSpecialistFreePeriods[4][1] = True
    scienceSpecialistFreePeriods[4][2] = True
    scienceSpecialistFreePeriods[7][3] = True
    scienceSpecialistFreePeriods[7][4] = True

    specialists = [
        Specialist(0, "Anglais", englishSpecialistFreePeriods),
        Specialist(1, "Frank", frankSpecialistFreePeriods),
        Specialist(2, "Musique 2", otherMusicSpecialistFreePeriods),
        Specialist(3, "Éduc 1", all_period_available()),
        Specialist(4, "Éduc 2", all_period_available()),
        Specialist(5, "Science", scienceSpecialistFreePeriods)
    ]

    locals = [
        Local(0, "Anglais Alizés", 0, {3, 4, 5, 6, 7, 8, 9, 10, 11}, {0}),
        Local(1, "Anglais Mousserons", 1, {12, 13, 14, 17, 18, 19}, {0}),
        Local(2, "Musique Alizés", 0, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}, {1, 2}),
        Local(3, "Musique Mousserons", 1, {12, 13, 14, 15, 16, 17, 18, 19}, {1}),
        Local(4, "Éduc Alizés", 0, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}, {3, 4}),
        Local(5, "Éduc Mousserons", 1, {12, 13, 14, 15, 16, 17, 18, 19}, {4}),
        Local(6, "Science Mousserons", 1, {15, 16}, {5})
    ]

    return ClassesAndResources(school, groups, specialists, locals, {1: getHalfTimeTutorHardCost})