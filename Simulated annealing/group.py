class Group:
    def __init__(self, id, name, level, needsBySubject):
        self.id = id
        self.name = name
        self.level = level
        self.needsBySubject = needsBySubject

    def toString(self):
        return "Group#" + str(self.id) + " '" + self.name + "', level: " + str(self.level) + ", needs: " + str(self.needsBySubject)