from classesAndResources import ClassesAndResources
from specialist import Specialist
from group import Group
from problemInstances import school1
import numpy as np

def class1Instance():

    school = school1.school1Instance()

    groups = []
    for groupId in range(6):
        groups.append(Group(groupId, "Year " + str(groupId + 1), np.asarray([4, 3, 2])))

    specialists = [
        Specialist(0, "english teacher", [[True]*school.periodsInDay]*school.daysInCycle, 0),
        Specialist(1, "physical education teacher", [[True]*school.periodsInDay]*school.daysInCycle, 1),
        Specialist(2, "music teacher", [[True]*school.periodsInDay]*school.daysInCycle, 2)
    ]

    return ClassesAndResources(school, groups, specialists)