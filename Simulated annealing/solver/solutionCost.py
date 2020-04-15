import numpy as np

class SolutionCost:
    def __init__(self, scores, details):
        self.scores = scores
        self.details = details

    def lowerOrEqualTo(self, solutionScore):
        diffs = self.scores - solutionScore.scores
        return diffs[np.argmax(diffs != 0)] <= 0

    def equalsTo(self, solutionScore):
        return np.array_equal(self.scores, solutionScore.scores)

    def deepEquals(self, solutionScore):
        return self.equalsTo(solutionScore) and np.array_equal(self.details, solutionScore.details)

    def isPerfect(self, upToIndex=None):
        if upToIndex == None:
            return np.sum(self.scores) == 0
        return np.sum(self.scores[:upToIndex+1]) == 0

    def magnitude(self):
        argMax = np.argmax(self.scores != 0)
        return argMax if self.scores[argMax] != 0 else len(self.scores) + 1

    def highestMagnitude(self):
        return self.scores[np.argmax(self.scores != 0)]

    @staticmethod
    def getDisplayHeader():
        return "{0:<19}{1:<19}{2:<35}{3:<31}{4}".format("Hard Constraints |",
                                                        "Soft Constraints ->",
                                                        "Spreading Free Periods Across... |",
                                                        "Spreading Subjects Across... |",
                                                        "Levels")

    def toString(self):
        scoresTab = "   {0:<5}|   {1:<5}|     {2:<18}Days: {3:<8}Periods: {4:<7}|  Days: {5:<7}Periods: {6:<6}|  {7:<8}".format(
            int(self.scores[0]),
            int(self.scores[1]),
            round(self.scores[2], 5),
            int(self.details[0] / 14500),
            int(self.details[1] / 3200),
            int(self.details[2] / 5900),
            int(self.details[3] / 75),
            int(self.details[4] / 3500))
        return scoresTab
