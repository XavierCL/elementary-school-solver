from problemInstances import classes2
from problemInstances import frankClasses

import scheduleEditor.uiSolver as uiSolver

import solver.solutionInstance as solutionInstance
import solver.solutionCost as solutionCost

import numpy as np

import scheduleEditor.hidding as hidding

from kivy.app import App
from kivy.clock import mainthread
from kivy.core.window import Window

from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView

from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionGroup, ActionButton

from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label


class ScheduleEditor(App):
    def __init__(self):
        App.__init__(self)

        # todo: Import csv from a button
        self.solver = uiSolver.UiSolver(classes2.classes2(), 5.0, 5.0)
        self.appStopped = False

        # todo: Import solution from csv
        # for now default empty is generated in the solver

        self.addButtons = [[[None for _ in range(self.solver.classesAndResources.school.periodsInDay)] for _ in range(self.solver.classesAndResources.school.daysInCycle)] for _ in self.solver.classesAndResources.specialists]
        self.groupDropdowns = [[[None for _ in range(self.solver.classesAndResources.school.periodsInDay)] for _ in range(self.solver.classesAndResources.school.daysInCycle)] for _ in self.solver.classesAndResources.specialists]
        self.groupsButtons = [[[[None for _ in self.solver.classesAndResources.groups] for _ in range(self.solver.classesAndResources.school.periodsInDay)] for _ in range(self.solver.classesAndResources.school.daysInCycle)] for _ in self.solver.classesAndResources.specialists]
        self.localDropdowns = [[[None for _ in range(self.solver.classesAndResources.school.periodsInDay)] for _ in range(self.solver.classesAndResources.school.daysInCycle)] for _ in self.solver.classesAndResources.specialists]
        self.localsButtons = [[[[None for _ in self.solver.classesAndResources.locals] for _ in range(self.solver.classesAndResources.school.periodsInDay)] for _ in range(self.solver.classesAndResources.school.daysInCycle)] for _ in self.solver.classesAndResources.specialists]
        self.deleteButtons = [[[None for _ in range(self.solver.classesAndResources.school.periodsInDay)] for _ in range(self.solver.classesAndResources.school.daysInCycle)] for _ in self.solver.classesAndResources.specialists]

        self.hiddenGroupSelections = [[[None for _ in range(self.solver.classesAndResources.school.periodsInDay)] for _ in range(self.solver.classesAndResources.school.daysInCycle)] for _ in self.solver.classesAndResources.specialists]
        self.hiddenLocalSelections = [[[None for _ in range(self.solver.classesAndResources.school.periodsInDay)] for _ in range(self.solver.classesAndResources.school.daysInCycle)] for _ in self.solver.classesAndResources.specialists]

    def on_stop(self):
        self.appStopped = True
        self.solver.stop()

    def startSolver(self):
        self.disablePeriodGrid(True)
        self.solver.start()

    def stopSolver(self):
        self.solver.stop()
        self.disablePeriodGrid(False)

    # Might be called from a worker thread, need to change the thread to the UI one to update the buttons
    @mainthread
    def updateVisualSolution(self, visualSolution: solutionInstance.SolutionInstance):
        if not self.appStopped:
            self.costLabel.text=solutionCost.SolutionCost.getDisplayHeader() + "\n" + visualSolution.getTotalCost().toString()

            for day in range(self.solver.classesAndResources.school.daysInCycle):
                for period in range(self.solver.classesAndResources.school.periodsInDay):
                    for specialist in self.solver.classesAndResources.specialists:
                        groupAndLocal = np.where(visualSolution.meetByPeriodByDayByLocalBySubjectByGroup[:, specialist.id, :, day, period])
                        if len(groupAndLocal[0]) == 0:
                            self.deleteButtons[specialist.id][day][period].trigger_action(duration=0)
                        else:
                            self.addButtons[specialist.id][day][period].trigger_action(duration=0)
                            self.groupsButtons[specialist.id][day][period][groupAndLocal[0][0]].trigger_action(duration=0)
                            self.localsButtons[specialist.id][day][period][groupAndLocal[1][0]].trigger_action(duration=0)

    @mainthread
    def updateVisualSolutionCost(self, visualSolutionCost: solutionCost.SolutionCost):
        if not self.appStopped:
            self.costLabel.text=solutionCost.SolutionCost.getDisplayHeader() + "\n" + visualSolutionCost.toString()

    def build(self):

        # todo: make classes and resources modifiable through UI and exportable
        # todo: make soft constraint editable throught the UI, and savable
        # todo: make hard constraint opt-out using checkboxes

        self.title = 'Elementary school solver'

        actionBar = self.buildActionBar()
        periodGrid = self.buildPeriodGrid()

        rootBoxLayout = BoxLayout(orientation='vertical', size_hint=(None, None), size=(Window.width, Window.height))
        rootBoxLayout.add_widget(actionBar)
        rootBoxLayout.add_widget(periodGrid)

        Window.bind(on_resize=lambda window, x, y: setattr(rootBoxLayout, 'size', (x, y)))

        self.solver.onVisualSolutionUpdated(self.updateVisualSolution)
        self.solver.onCostUpdated(self.updateVisualSolutionCost)

        return rootBoxLayout

    def buildActionBar(self):
        actionView = ActionView()
        
        actionView.use_separator = True
        actionView.add_widget(ActionPrevious(with_previous=False))

        self.costLabel = ActionButton(text='Cost: Yet to be computed', disabled=True, font_name='RobotoMono-Regular.ttf')
        actionView.add_widget(self.costLabel)

        solverGroup = ActionGroup(text='Solver', mode='spinner')

        startSolverButton = ActionButton(text='Start solver')
        startSolverButton.bind(on_release=lambda instance: self.startSolver())
        solverGroup.add_widget(startSolverButton)

        stopSolverButton = ActionButton(text='Stop solver')
        stopSolverButton.bind(on_release=lambda instance: self.stopSolver())
        solverGroup.add_widget(stopSolverButton)

        actionView.add_widget(solverGroup)

        actionBar = ActionBar()
        actionBar.add_widget(actionView)

        return actionBar

    def disablePeriodGrid(self, disabled=True):
        for buttonGroup in [self.addButtons, self.groupDropdowns, self.localDropdowns, self.deleteButtons]:
            for specialist in self.solver.classesAndResources.specialists:
                for day in range(self.solver.classesAndResources.school.daysInCycle):
                    for period in range(self.solver.classesAndResources.school.periodsInDay):
                        hidding.setHiddenAttr(buttonGroup[specialist.id][day][period], 'disabled', disabled)

    def buildPeriodGrid(self):

        def createAddMeetingButton(specialist, day, period):
            addButton = Button()

            def addButtonCallback(button):
                self.solver.addSpecialistDayPeriodMeetingAtGroupAndLocal(specialist, day, period, self.hiddenGroupSelections[specialist][day][period], self.hiddenLocalSelections[specialist][day][period])
                hidding.hide_widget(addButton, True)
                hidding.hide_widget(self.groupDropdowns[specialist][day][period], False)
                hidding.hide_widget(self.localDropdowns[specialist][day][period], False)
                hidding.hide_widget(self.deleteButtons[specialist][day][period], False)

            addButton.bind(on_release=addButtonCallback)

            self.addButtons[specialist][day][period] = addButton

            return addButton

        def createGroupDropdown(specialist, day, period):
            dropdown = DropDown()
            for group in self.solver.classesAndResources.groups:
                groupButton = Button(text=group.name, size_hint_y=None, height=30)
                groupButton.solverGroup = group

                def groupButtonCallback(button):
                    group = button.solverGroup
                    self.solver.changeSpecialistDayPeriodGroup(specialist, day, period, self.hiddenLocalSelections[specialist][day][period], self.hiddenGroupSelections[specialist][day][period], group.id)
                    self.hiddenGroupSelections[specialist][day][period] = group.id
                    dropdown.select(group)

                groupButton.bind(on_release=groupButtonCallback)
                self.groupsButtons[specialist][day][period][group.id] = groupButton
                dropdown.add_widget(groupButton)

            dropdownButton = Button(text=self.solver.classesAndResources.groups[0].name, size_hint_x=None)
            dropdownButton.bind(on_release=lambda instance: dropdown.open(instance))
            dropdown.bind(on_select=lambda instance, group: setattr(dropdownButton, 'text', group.name))
            dropdownButton.width=200

            self.groupDropdowns[specialist][day][period] = dropdownButton
            self.hiddenGroupSelections[specialist][day][period] = 0
            hidding.hide_widget(dropdownButton, True)

            return dropdownButton

        def createLocalDropdown(specialist, day, period):
            localWidth = 400
            dropdown = DropDown(auto_width=False, size_hint_x=None, width=localWidth)
            for local in self.solver.classesAndResources.locals:
                localButton = Button(text=str(local.id) + " - " + local.name, size_hint=(None, None), size=(localWidth, 30))
                localButton.solverLocal = local

                def localButtonCallback(button):
                    local = button.solverLocal
                    self.solver.changeSpecialistDayPeriodLocal(specialist, day, period, self.hiddenGroupSelections[specialist][day][period], self.hiddenLocalSelections[specialist][day][period], local.id)
                    self.hiddenLocalSelections[specialist][day][period] = local.id
                    dropdown.select(local)
                
                localButton.bind(on_release=localButtonCallback)
                self.localsButtons[specialist][day][period][local.id] = localButton
                dropdown.add_widget(localButton)

            dropdownButton = Button(text=str(self.solver.classesAndResources.locals[0].id), size_hint_x=None)
            dropdownButton.bind(on_release=lambda instance: dropdown.open(instance))
            dropdown.bind(on_select=lambda instance, local: setattr(dropdownButton, 'text', str(local.id)))
            dropdownButton.width=30

            self.localDropdowns[specialist][day][period] = dropdownButton
            self.hiddenLocalSelections[specialist][day][period] = 0
            hidding.hide_widget(dropdownButton, True)

            return dropdownButton

        def createDeleteMeetingButton(specialist, day, period):
            deleteButton = Button(text='X', size_hint_x=None)

            def deleteButtonCallback(button):
                self.solver.removeSpecialistDayPeriodMeeting(specialist, day, period)

                hidding.hide_widget(self.addButtons[specialist][day][period], False)
                hidding.hide_widget(self.groupDropdowns[specialist][day][period], True)
                hidding.hide_widget(self.localDropdowns[specialist][day][period], True)
                hidding.hide_widget(deleteButton, True)

            deleteButton.bind(on_release=deleteButtonCallback)
            deleteButton.width=30

            self.deleteButtons[specialist][day][period] = deleteButton
            hidding.hide_widget(deleteButton, True)

            return deleteButton

        def createCell(specialist, day, period):
            addMeetingButton = createAddMeetingButton(specialist, day, period)
            groupButton = createGroupDropdown(specialist, day, period)
            localButton = createLocalDropdown(specialist, day, period)
            removeMeetingButton = createDeleteMeetingButton(specialist, day, period)

            cellLayout = StackLayout(size_hint_x=None, width=hidding.getHiddenAttr(groupButton, 'width') + hidding.getHiddenAttr(localButton, 'width') + hidding.getHiddenAttr(removeMeetingButton, 'width'))

            cellLayout.add_widget(addMeetingButton)
            cellLayout.add_widget(groupButton)
            cellLayout.add_widget(localButton)
            cellLayout.add_widget(removeMeetingButton)
            return cellLayout

        # Should be using a relative layout instead and place buttons manually using pixel positions
        periodGrid = GridLayout(cols=self.solver.classesAndResources.school.daysInCycle + 1, rows=len(self.solver.classesAndResources.specialists)*self.solver.classesAndResources.school.periodsInDay + self.solver.classesAndResources.school.periodsInDay, size_hint=(None, None), size=(self.solver.classesAndResources.school.daysInCycle*265 + 150, len(self.solver.classesAndResources.specialists) * self.solver.classesAndResources.school.periodsInDay * 36 + 36))

        periodGrid.add_widget(Label())
        for cycleDay in range(self.solver.classesAndResources.school.daysInCycle):
            dayLayout = RelativeLayout()
            dayLabel = Label(text=str(cycleDay + 1), size_hint=(None, None), pos_hint={'center_x': 0.5, 'center_y': 0.5})
            dayLabel.bind(texture_size=dayLabel.setter('size'))
            dayLayout.add_widget(dayLabel)
            periodGrid.add_widget(dayLayout)

        for period in range(self.solver.classesAndResources.school.periodsInDay):
            for specialist in self.solver.classesAndResources.specialists:

                specialistLayout = RelativeLayout(size_hint_x=(None))
                specialistLabel = Label(text=specialist.name, size_hint=(None, None), pos_hint={'center_x': 0.5, 'center_y': 0.5})
                specialistLabel.bind(texture_size=specialistLabel.setter('size'))
                specialistLabel.bind(width=specialistLayout.setter('width'))
                specialistLayout.add_widget(specialistLabel)
                periodGrid.add_widget(specialistLayout)

                for day in range(self.solver.classesAndResources.school.daysInCycle):
                    periodGrid.add_widget(createCell(specialist.id, day, period))
            if period != self.solver.classesAndResources.school.periodsInDay - 1:
                for day in range(self.solver.classesAndResources.school.daysInCycle + 1):
                    periodGrid.add_widget(Label(size_hint_y=None, height=30))

        periodScrollViewer = ScrollView()
        periodScrollViewer.add_widget(periodGrid)

        return periodScrollViewer