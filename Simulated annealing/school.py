class School:
    def __init__(self, daysInCycle, periodsInAm, periodsInPm):
        self.daysInCycle = daysInCycle
        self.periodsInAm = periodsInAm
        self.periodsInPm = periodsInPm
        self.periodsInDay = self.periodsInAm + self.periodsInPm
        self.totalPeriodCount = self.periodsInDay * daysInCycle

    def toString(self):
        return "Days in cycle: " + str(self.daysInCycle) + """
Periods in am: """ + str(self.periodsInAm) + """
Periods in pm: """ + str(self.periodsInPm)