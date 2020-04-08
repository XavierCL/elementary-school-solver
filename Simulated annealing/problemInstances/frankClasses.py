from classesAndResources import ClassesAndResources
from specialist import Specialist
from group import Group
from local import Local
from problemInstances import school1
import numpy as np

def getFrankHalfTimeTutorHardCost(solutionInstance):
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
        Group(0, "Présco Annabelle", 0, np.asarray([0, 0, 1, 2, 0, 0]), enseignantTempsPleinDispos),
        Group(1, "Présco Jo-Annie", 0, np.asarray([0, 0, 1, 2, 0, 0]), enseignantTempsPleinDispos),
        Group(2, "Présco Nadine", 0, np.asarray([0, 0, 1, 2, 0, 0]), enseignantTempsPleinDispos),
        
        Group(3, "1 - Marie-Ève", 1, np.asarray([2, 0, 3, 4, 0, 0]), enseignantTempsPleinDispos),
        Group(4, "1 - Chantal", 1, np.asarray([2, 0, 3, 4, 0, 0]), enseignantTempsPleinDispos),
        
        Group(5, "2 - Valérie", 2, np.asarray([2, 0, 3, 4, 0, 0]), enseignantTempsPleinDispos),
        Group(6, "2 - Josée", 2, np.asarray([2, 3, 0, 4, 0, 0]), enseignantTempsPleinDispos),

        Group(7, "3 - Karyne", 3, np.asarray([2, 3, 0, 4, 0, 0]), enseignantTempsPleinDispos),
        Group(8, "3 - Marie", 3, np.asarray([2, 3, 0, 4, 0, 0]), enseignantTempsPleinDispos),
        Group(9, "3 - Anne", 3, np.asarray([2, 3, 0, 0, 4, 0]), enseignantTempsPleinDispos),
        
        Group(10, "4 - Anne-Marie", 4, np.asarray([3, 2, 0, 4, 0, 0]), enseignantTempsPleinDispos),
        Group(11, "4 - Karine", 4, np.asarray([3, 2, 0, 4, 0, 0]), enseignantTempsPleinDispos),
        
        Group(12, "5 - Brigitte", 5, np.asarray([3, 2, 0, 0, 4, 0]), enseignantTempsPleinDispos),
        Group(13, "5 - Jean-Yves", 5, np.asarray([3, 2, 0, 0, 4, 0]), enseignantTempsPleinDispos),
        
        Group(14, "5 et 6 - Marie-Ève M.", 5.5, np.asarray([3, 2, 0, 0, 4, 0]), enseignantTempsPleinDispos),

        Group(15, "6 - Annie", 6, np.asarray([0, 2, 0, 0, 4, 3]), enseignantTempsPleinDispos),
        Group(16, "6 - France", 6, np.asarray([0, 2, 0, 0, 4, 3]), enseignantTempsPleinDispos),

        Group(17, "CISA - Isabelle", 7, np.asarray([1, 2, 0, 0, 6, 0]), adaptationIsabelleDispos),
        Group(18, "CISA - Marie-Pier", 7, np.asarray([1, 2, 0, 0, 6, 0]), adaptationMariePierDispos),
        Group(19, "CISA - Marie-Ève C.", 7, np.asarray([1, 3, 0, 0, 5, 0]), enseignantTempsPleinDispos)
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
        Specialist(1, "Frank (musique) gr2.06-4.11(Mousserons) gr5.12+(Alizés)", frankSpecialistFreePeriods),
        Specialist(2, "Musique (29% gr2.05 et moins)", otherMusicSpecialistFreePeriods),
        Specialist(3, "Éduc 1 (Alizés gr3.08 et moins)", all_period_available()),
        Specialist(4, "Éduc 2 (Mousserons + gr3.09)", all_period_available()),
        Specialist(5, "Science teacher (dispo J2-J8 PM, J5 AM)", scienceSpecialistFreePeriods)
    ]

    locals = [
        Local(0, "First premise english room (Alizés)", 0, {3, 4, 5, 6, 7, 8, 9, 10, 11}, {0}),
        Local(1, "Second premise english room (Mousserons)", 1, {12, 13, 14, 17, 18, 19}, {0}),
        Local(2, "First premise music room (Alizés)", 0, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}, {1, 2}),
        Local(3, "Second premise music room (Mousserons)", 1, {12, 13, 14, 15, 16, 17, 18, 19}, {1}),
        Local(4, "First premise PE room (Alizés)", 0, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}, {3, 4}),
        Local(5, "Second premise PE room (Mousserons)", 1, {12, 13, 14, 15, 16, 17, 18, 19}, {4}),
        Local(6, "First premise Science room (Mousserons)", 1, {15, 16}, {5})
    ]

    return ClassesAndResources(school, groups, specialists, locals, {1: getFrankHalfTimeTutorHardCost})