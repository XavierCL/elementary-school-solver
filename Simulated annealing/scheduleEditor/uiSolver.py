import solver.solver as solver
import solver.solutionInstance as solutionInstance
import time

import numpy as np

import threading

class UiSolver:
    def __init__(self, classesAndResources, visualSolutionRefreshRateInSecond, lastSolutionCostRefreshRateInSecond):
        self.classesAndResources = classesAndResources
        self.visualSolutionRefreshRateInSecond = visualSolutionRefreshRateInSecond
        self.lastSolutionCostRefreshRateInSecond = lastSolutionCostRefreshRateInSecond
        self.visualSolutionUpdatedCallback = lambda: None
        self.lastSolutionCostUpdatedCallback = lambda: None

        self._lastSolution = solutionInstance.SolutionInstance(classesAndResources, np.zeros((len(classesAndResources.groups), len(classesAndResources.specialists), len(classesAndResources.locals), classesAndResources.school.daysInCycle, classesAndResources.school.periodsInDay)).astype(np.bool))
        self._visualSolution = self._lastSolution
        self._visualCost = self._lastSolution.getTotalCost()

        self._isRunning = False
        self._shouldRun = False
        self._solverThread = None
        self._uiUpdaterTimer = None
        self._costUpdaterTimer = None

    def changeSpecialistDayPeriodGroup(self, specialist, day, period, local, oldGroupId, newGroupId):
        if not self._isRunning:
            self._visualSolution = self._visualSolution.assignGroupToSpecialistDayAndPeriod(specialist, day, period, local, oldGroupId, newGroupId)
            self._lastSolution = self._visualSolution
            self._visualCost = self._lastSolution.getTotalCost()
            self.lastSolutionCostUpdatedCallback(self._visualCost)

    def changeSpecialistDayPeriodLocal(self, specialist, day, period, group, oldLocalId, newLocalId):
        if not self._isRunning:
            self._visualSolution = self._visualSolution.assignLocalToSpecialistDayAndPeriod(specialist, day, period, group, oldLocalId, newLocalId)
            self._lastSolution = self._visualSolution
            self._visualCost = self._lastSolution.getTotalCost()
            self.lastSolutionCostUpdatedCallback(self._visualCost)

    def removeSpecialistDayPeriodMeeting(self, specialist, day, period):
        if not self._isRunning:
            self._visualSolution = self._visualSolution.removeSpecialistDayPeriodMeeting(specialist, day, period)
            self._lastSolution = self._visualSolution
            self._visualCost = self._lastSolution.getTotalCost()
            self.lastSolutionCostUpdatedCallback(self._visualCost)

    def addSpecialistDayPeriodMeetingAtGroupAndLocal(self, specialist, day, period, group, local):
        if not self._isRunning:
            self._visualSolution = self._visualSolution.addSpecialistDayPeriodMeetingWithGroupAtLocal(specialist, day, period, group, local)
            self._lastSolution = self._visualSolution
            self._visualCost = self._lastSolution.getTotalCost()
            self.lastSolutionCostUpdatedCallback(self._visualCost)

    def start(self):
        if self._shouldRun:
            return

        self._shouldRun = True
        self._isRunning = True
        self._solverThread = threading.Thread(target=self._runSolver)
        self._solverThread.start()
        self._runVisualUpdater()
        self._runCostUpdater()

    def askToStop(self):
        if not self._shouldRun:
            return

        self._shouldRun = False
        self._uiUpdaterTimer.cancel()
        self._costUpdaterTimer.cancel()
        self._solverThread.join()
        self._updateVisualIfLastSolutionChanged()

    def uiStopped(self):
        self._isRunning = False

    def onVisualSolutionUpdated(self, callback):
        self.visualSolutionUpdatedCallback = callback
        self.visualSolutionUpdatedCallback(self._visualSolution)

    def onCostUpdated(self, callback):
        self.lastSolutionCostUpdatedCallback = callback
        self.lastSolutionCostUpdatedCallback(self._lastSolution.getTotalCost())

    def _runSolver(self):
        solver.optimizeSolutionInstance(self._lastSolution, 4, 0.99765, lambda better: setattr(self, '_lastSolution', better), lambda: self._shouldRun, time.time() * 1000.)

    def _runVisualUpdater(self):
        if self._shouldRun:
            self._updateVisualIfLastSolutionChanged()
            self._uiUpdaterTimer = threading.Timer(self.visualSolutionRefreshRateInSecond, self._runVisualUpdater)

            # To avoid race condition where the stop would be called before the new instantiation of the timer and after the running check is done
            if self._shouldRun:
                self._uiUpdaterTimer.start()

    def _runCostUpdater(self):
        if self._shouldRun:
            self._updateVisualCostIfLastSolutionChanged()
            self._costUpdaterTimer = threading.Timer(self.lastSolutionCostRefreshRateInSecond, self._runCostUpdater)

            # To avoid race condition where the stop would be called before the new instantiation of the timer and after the running check is done
            if self._shouldRun:
                self._costUpdaterTimer.start()

    def _updateVisualIfLastSolutionChanged(self):
        if not self._visualSolution.equals(self._lastSolution):
            self._visualSolution = self._lastSolution
            self.visualSolutionUpdatedCallback(self._visualSolution)

    def _updateVisualCostIfLastSolutionChanged(self):
        lastSolutionScore = self._lastSolution.getTotalCost()
        if not self._visualCost.deepEquals(lastSolutionScore):
            self._visualCost = lastSolutionScore
            self.lastSolutionCostUpdatedCallback(self._visualCost)