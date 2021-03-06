from solver.school import School
import numpy as np

class ClassesAndResources:
    def __init__(self, school, groups, specialists, locals, customConstraints):
        self.school: School = school
        self.groups = groups
        self.specialists = specialists
        self.locals = locals
        self.customConstraints = customConstraints
        
        self.groupsNeeds = np.stack(map(lambda group: group.needsBySubject, groups), axis=0)
        self.premises = set()
        self.premiseByLocal = np.asarray([local.premise for local in locals])

        self.localsBySpecialistAndGroup = [[set() for _ in range(len(specialists))] for _ in range(len(groups))]

        for local in locals:
            self.premises.add(local.premise)
            for group in local.allowedGroups:
                for specialist in local.allowedSpecialists:
                    self.localsBySpecialistAndGroup[group][specialist].add(local.id)

        self.localListBySpecialistAndGroup = [[list(self.localsBySpecialistAndGroup[group][specialist]) for specialist in range(len(specialists))] for group in range(len(groups))]

        self.specialistsFreePeriods = np.stack(map(lambda specialist: specialist.freePeriods, specialists)).astype(np.int32)
        self.premiseCount = len(self.premises)
        self.maxLevel = np.max(list(map(lambda group: group.level, groups)))

        self.levelByGroup = np.asarray([group.level for group in groups])

        self.tutorFreePeriods = np.stack(map(lambda group: group.tutorFreePeriods, groups)).astype(np.bool)

    def getDepthCost(self, solutionInstance, depth):
        if depth in self.customConstraints:
            return self.customConstraints[depth](solutionInstance)
        else:
            return 0

    def toString(self):
        return self.school.toString() + """

""" + "\n".join(map(lambda group: group.toString(), self.groups)) + """

""" + "\n".join(map(lambda specialist: specialist.toString(), self.specialists)) + """

""" + "\n".join(map(lambda local: local.toString(), self.locals))