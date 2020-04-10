from problemInstances import classes2
from problemInstances import frankClasses
import solver.solutionInstance as solutionInstance

import numpy as np

import scheduleEditor.hidding as hidding

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

class TutorialApp(App):
    def build(self):

        # todo: Import json from a button
        classInstance = frankClasses.frankClassesInstance()

        # todo: Import json from a button
        self.lastSolution = solutionInstance.SolutionInstance(classInstance, np.zeros((len(classInstance.groups), len(classInstance.specialists), len(classInstance.locals), classInstance.school.daysInCycle, classInstance.school.periodsInDay)).astype(np.bool))

        # todo: make classes and resources modifiable through UI and exportable
        # todo: make soft constraint editable throught the UI, and savable
        # todo: make hard constraint opt-out using checkboxes

        # todo make solver runnable on the last solution

        def changeSpecialistDayPeriodGroup(specialist, day, period, local, oldGroupId, newGroupId):
            self.lastSolution = self.lastSolution.assignGroupToSpecialistDayAndPeriod(specialist, day, period, local, oldGroupId, newGroupId)

        def changeSpecialistDayPeriodLocal(specialist, day, period, group, oldLocalId, newLocalId):
            self.lastSolution = self.lastSolution.assignLocalToSpecialistDayAndPeriod(specialist, day, period, group, oldLocalId, newLocalId)

        def removeSpecialistDayPeriodMeeting(specialist, day, period):
            self.lastSolution = self.lastSolution.removeSpecialistDayPeriodMeeting(specialist, day, period)

        def addSpecialistDayPeriodMeetingAtGroupAndLocal(specialist, day, period, group, local):
            self.lastSolution = self.lastSolution.addSpecialistDayPeriodMeetingWithGroupAtLocal(specialist, day, period, group, local)

        addButtons = [[[None for _ in range(classInstance.school.periodsInDay)] for _ in range(classInstance.school.daysInCycle)] for _ in classInstance.specialists]
        groupDropdowns = [[[None for _ in range(classInstance.school.periodsInDay)] for _ in range(classInstance.school.daysInCycle)] for _ in classInstance.specialists]
        localDropdowns = [[[None for _ in range(classInstance.school.periodsInDay)] for _ in range(classInstance.school.daysInCycle)] for _ in classInstance.specialists]
        deleteButtons = [[[None for _ in range(classInstance.school.periodsInDay)] for _ in range(classInstance.school.daysInCycle)] for _ in classInstance.specialists]

        hiddenGroupSelections = [[[None for _ in range(classInstance.school.periodsInDay)] for _ in range(classInstance.school.daysInCycle)] for _ in classInstance.specialists]
        hiddenLocalSelections = [[[None for _ in range(classInstance.school.periodsInDay)] for _ in range(classInstance.school.daysInCycle)] for _ in classInstance.specialists]

        def createAddMeetingButton(specialist, day, period):
            addButton = Button()

            def addButtonCallback(button):
                addSpecialistDayPeriodMeetingAtGroupAndLocal(specialist, day, period, hiddenGroupSelections[specialist][day][period], hiddenLocalSelections[specialist][day][period])
                hidding.hide_widget(addButton, True)
                hidding.hide_widget(groupDropdowns[specialist][day][period], False)
                hidding.hide_widget(localDropdowns[specialist][day][period], False)
                hidding.hide_widget(deleteButtons[specialist][day][period], False)

            addButton.bind(on_release=addButtonCallback)

            addButtons[specialist][day][period] = addButton

            return addButton

        def createGroupDropdown(specialist, day, period):
            dropdown = DropDown()
            for group in classInstance.groups:
                groupButton = Button(text=group.name, size_hint_y=None, height=30)
                groupButton.solverGroup = group

                def groupButtonCallback(button):
                    group = button.solverGroup
                    changeSpecialistDayPeriodGroup(specialist, day, period, hiddenLocalSelections[specialist][day][period], hiddenGroupSelections[specialist][day][period], group.id)
                    hiddenGroupSelections[specialist][day][period] = group.id
                    dropdown.select(group)

                groupButton.bind(on_release=groupButtonCallback)
                dropdown.add_widget(groupButton)

            dropdownButton = Button(text=classInstance.groups[0].name, size_hint_x=None)
            dropdownButton.bind(on_release=lambda instance: dropdown.open(instance))
            dropdown.bind(on_select=lambda instance, group: setattr(dropdownButton, 'text', group.name))
            dropdownButton.width=200

            groupDropdowns[specialist][day][period] = dropdownButton
            hiddenGroupSelections[specialist][day][period] = 0
            hidding.hide_widget(dropdownButton, True)

            return dropdownButton

        def createLocalDropdown(specialist, day, period):
            dropdown = DropDown()
            for local in classInstance.locals:
                localButton = Button(text=local.name, size_hint_y=None, height=30)
                localButton.solverLocal = local

                def localButtonCallback(button):
                    local = button.solverLocal
                    changeSpecialistDayPeriodLocal(specialist, day, period, hiddenGroupSelections[specialist][day][period], hiddenLocalSelections[specialist][day][period], local.id)
                    hiddenLocalSelections[specialist][day][period] = local.id
                    dropdown.select(local)
                
                localButton.bind(on_release=localButtonCallback)
                dropdown.add_widget(localButton)

            dropdownButton = Button(text=classInstance.locals[0].name, size_hint_x=None)
            dropdownButton.bind(on_release=lambda instance: dropdown.open(instance))
            dropdown.bind(on_select=lambda instance, local: setattr(dropdownButton, 'text', local.name))
            dropdownButton.width=200

            localDropdowns[specialist][day][period] = dropdownButton
            hiddenLocalSelections[specialist][day][period] = 0
            hidding.hide_widget(dropdownButton, True)

            return dropdownButton

        def createDeleteMeetingButton(specialist, day, period):
            deleteButton = Button(text='X', size_hint_x=None)

            def deleteButtonCallback(button):
                removeSpecialistDayPeriodMeeting(specialist, day, period)

                hidding.hide_widget(addButtons[specialist][day][period], False)
                hidding.hide_widget(groupDropdowns[specialist][day][period], True)
                hidding.hide_widget(localDropdowns[specialist][day][period], True)
                hidding.hide_widget(deleteButton, True)

            deleteButton.bind(on_release=deleteButtonCallback)
            deleteButton.width=30

            deleteButtons[specialist][day][period] = deleteButton
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
        rootGrid = GridLayout(cols=classInstance.school.daysInCycle + 1, rows=len(classInstance.specialists)*classInstance.school.periodsInDay + classInstance.school.periodsInDay, size_hint=(None, None), size=(classInstance.school.daysInCycle*435 + 150, len(classInstance.specialists) * classInstance.school.periodsInDay * 36 + 36))
        # rootGrid.bind(minimum_height=rootGrid.setter('height'))
        # rootGrid.bind(minimum_width=rootGrid.setter('width'))

        rootGrid.add_widget(Label())
        for cycleDay in range(classInstance.school.daysInCycle):
            dayLayout = RelativeLayout()
            dayLabel = Label(text=str(cycleDay + 1), size_hint=(None, None), pos_hint={'center_x': 0.5, 'center_y': 0.5})
            dayLabel.bind(texture_size=dayLabel.setter('size'))
            dayLayout.add_widget(dayLabel)
            rootGrid.add_widget(dayLayout)

        for period in range(classInstance.school.periodsInDay):
            for specialist in classInstance.specialists:

                specialistLayout = RelativeLayout(size_hint_x=(None))
                specialistLabel = Label(text=specialist.name, size_hint=(None, None), pos_hint={'center_x': 0.5, 'center_y': 0.5})
                specialistLabel.bind(texture_size=specialistLabel.setter('size'))
                specialistLabel.bind(width=specialistLayout.setter('width'))
                specialistLayout.add_widget(specialistLabel)
                rootGrid.add_widget(specialistLayout)

                for day in range(classInstance.school.daysInCycle):
                    rootGrid.add_widget(createCell(specialist.id, day, period))
            if period != classInstance.school.periodsInDay - 1:
                for day in range(classInstance.school.daysInCycle + 1):
                    rootGrid.add_widget(Label(size_hint_y=None, height=30))

        rootScrollViewer = ScrollView(size_hint=(None, None), size=(Window.width, Window.height))
        Window.bind(on_resize=lambda window, x, y: setattr(rootScrollViewer, 'size', (x, y)))
        rootScrollViewer.add_widget(rootGrid)
        return rootScrollViewer