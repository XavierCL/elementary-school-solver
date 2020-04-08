class Local:
    def __init__(self, id, name, premise, allowedGroups, allowedSpecialists):
        self.id = id
        self.name = name
        self.premise = premise
        self.allowedGroups = allowedGroups
        self.allowedSpecialists = allowedSpecialists
        
    def toString(self):
        return "Local#" + str(self.id) + " '" + self.name + "' on premise " + str(self.premise) + ". Allowed groups: " + str(self.allowedGroups) + ", specialists: """ + str(self.allowedSpecialists)