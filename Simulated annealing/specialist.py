class Specialist:
    def __init__(self, id, name, freePeriods):
        self.id = id
        self.name = name
        self.freePeriods = freePeriods

    def toString(self):
        return "Specialist#" + str(self.id) + " " + self.name + " free on periods:\n" + str(self.freePeriods.T)