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

    def isPerfect(self, upToIndex=None):
        if upToIndex == None:
            return np.sum(self.scores) == 0
        return np.sum(self.scores[:upToIndex+1]) == 0

    def magnitude(self):
        argMax = np.argmax(self.scores != 0)
        return argMax if self.scores[argMax] != 0 else len(self.scores) + 1

    def highestMagnitude(self):
        return self.scores[np.argmax(self.scores != 0)]

    def toString(self):
        details = "" if self.details == None else ", details: " + str(self.details)
        return str(self.scores) + details