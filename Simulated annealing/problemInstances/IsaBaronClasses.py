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


def isaBaronClassesInstance():
    school = school1.school1Instance()

    def all_period_available():
        return np.ones((school.daysInCycle, school.periodsInDay)).astype(np.bool)

    def no_period_available():
        return np.zeros((school.daysInCycle, school.periodsInDay)).astype(np.bool)

    # Dispos (temps plein pour tous sauf CISA1 et CISA2)
    enseignantTempsPleinDispos = all_period_available()
    prescoMelanieDispos = all_period_available()
    prescoMelanieDispos[[2,7]] = False
    premiereCathyDispos = all_period_available()
    premiereCathyDispos[[4,9]] = False
    premiereMelanieDispos = all_period_available()
    premiereMelanieDispos[[0,5]] = False
    deuxiemeIngridDispos = all_period_available()
    deuxiemeIngridDispos[[3,8]] = False
    deuxEtTroisMarieClaudeDispos = all_period_available()
    deuxEtTroisMarieClaudeDispos[[0]] = False
    troisiemeIsabelleDispos = all_period_available()
    troisiemeIsabelleDispos[[0]] = False
    cinquiemeEmilieDispos = all_period_available()
    cinquiemeEmilieDispos[[0]] = False

    groups = [
        Group(0, "Présco Emmanuelle", 0, np.asarray([2, 0, 0, 0, 0, 0]), enseignantTempsPleinDispos),
        Group(1, "Présco Véro/Josée", 0, np.asarray([0, 2, 0, 0, 0, 0]), enseignantTempsPleinDispos),
        Group(2, "Présco Mélanie", 0, np.asarray([0, 2, 0, 0, 0, 0]), prescoMelanieDispos),

        Group(3, "1e Cathy", 1, np.asarray([0, 4, 3, 0, 0, 2]), premiereCathyDispos),
        Group(4, "1e Julie", 1, np.asarray([0, 4, 3, 0, 0, 2]), enseignantTempsPleinDispos),
        Group(5, "1e Mélanie", 1, np.asarray([0, 4, 3, 0, 0, 2]), premiereMelanieDispos),

        Group(6, "2e Sandra", 2, np.asarray([4, 0, 3, 0, 0, 2]), enseignantTempsPleinDispos),
        Group(7, "2e Ingrid", 2, np.asarray([4, 0, 3, 0, 0, 2]), deuxiemeIngridDispos),

        Group(8, "2-3e Marie-Claude", 2.5, np.asarray([4, 0, 3, 0, 0, 2]), deuxEtTroisMarieClaudeDispos),

        Group(9, "3e Isabelle", 3, np.asarray([4, 0, 3, 0, 0, 2]), troisiemeIsabelleDispos),
        Group(10, "3e Lisa", 3, np.asarray([4, 0, 3, 0, 0, 2]), enseignantTempsPleinDispos),

        Group(11, "3-4e Émilie", 3.5, np.asarray([0, 4, 3, 0, 0, 2]), enseignantTempsPleinDispos),

        Group(12, "4e Janie", 4, np.asarray([0, 4, 3, 0, 0, 2]), enseignantTempsPleinDispos),
        Group(13, "4e Sandra", 4, np.asarray([0, 4, 3, 0, 0, 2]), enseignantTempsPleinDispos),

        Group(14, "5e Caroline", 5, np.asarray([4, 0, 0, 3, 2, 0]), enseignantTempsPleinDispos),
        Group(15, "5e Émilie", 5, np.asarray([4, 0, 0, 3, 2, 0]), cinquiemeEmilieDispos),
        Group(16, "5e Josée", 5, np.asarray([4, 0, 0, 3, 2, 0]), enseignantTempsPleinDispos),

        Group(17, "6e Émilie", 6, np.asarray([4, 0, 3, 0, 2, 0]), enseignantTempsPleinDispos),
        Group(18, "6e Corinne", 6, np.asarray([4, 0, 3, 0, 2, 0]), enseignantTempsPleinDispos),
    ]

    educ2FreePeriods = all_period_available()
    educ2FreePeriods[[0, 2, 4, 7]] = False
    educ2FreePeriods[0][3] = True
    educ2FreePeriods[0][4] = True
    educ2FreePeriods[2][0] = True
    educ2FreePeriods[2][1] = True
    educ2FreePeriods[3][3] = False
    educ2FreePeriods[3][4] = False
    educ2FreePeriods[4][3] = True
    educ2FreePeriods[4][4] = True
    educ2FreePeriods[5][3] = False
    educ2FreePeriods[5][4] = False
    educ2FreePeriods[6][3] = False
    educ2FreePeriods[6][4] = False
    educ2FreePeriods[7][0] = True
    educ2FreePeriods[7][1] = True
    educ2FreePeriods[8][3] = False
    educ2FreePeriods[8][4] = False

    anglaisFreePeriods = all_period_available()
    anglaisFreePeriods[3][3] = False
    anglaisFreePeriods[3][4] = False
    anglaisFreePeriods[8][3] = False
    anglaisFreePeriods[8][4] = False

    universSocialFreePeriods = no_period_available()
    universSocialFreePeriods[[1, 5]] = True

    artDramatiqueFreePeriods = no_period_available()
    artDramatiqueFreePeriods[[3, 8]] = True

    musiqueFreePeriods = no_period_available()
    musiqueFreePeriods[[0, 2, 4, 6, 7]] = True
    musiqueFreePeriods[6][3] = False
    musiqueFreePeriods[6][4] = False
    musiqueFreePeriods[9][3] = True
    musiqueFreePeriods[9][4] = True

    specialists = [
        Specialist(0, "Éduc 1", all_period_available()),
        Specialist(1, "Éduc 2", educ2FreePeriods),
        Specialist(2, "Anglais", anglaisFreePeriods),
        Specialist(3, "Univers Social", universSocialFreePeriods),
        Specialist(4, "Art dram", artDramatiqueFreePeriods),
        Specialist(5, "Musique", musiqueFreePeriods)
    ]

    locals = [
        Local(0, "Éduc 1", 0, {0, 6, 7, 8, 9, 10, 14, 15, 16, 17, 18}, {0}),
        Local(1, "Éduc 2", 0, {1, 2, 3, 4, 5, 11, 12, 13}, {1}),
        Local(2, "Anglais", 0, {3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18}, {2}),
        Local(3, "Univers Social", 0, {14, 15, 16}, {3}),
        Local(4, "Art dram", 0, {14, 15, 16, 17, 18}, {4}),
        Local(5, "Musique", 0, {3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}, {5})
    ]

    return ClassesAndResources(school, groups, specialists, locals, {1: getFrankHalfTimeTutorHardCost})