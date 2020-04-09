from problemInstances import frankClasses
import solver.solutionInstance as solutionInstance

import numpy as np

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

def hide_widget(wid, dohide=True):
    if hasattr(wid, 'saved_hide_attrs'):
        if not dohide:
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled, wid.width, wid.size_hint_x = wid.saved_hide_attrs
            del wid.saved_hide_attrs
    elif dohide:
        wid.saved_hide_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled, wid.width, wid.size_hint_x
        wid.height, wid.size_hint_y, wid.opacity, wid.disabled, wid.width, wid.size_hint_x = 0, None, 0, True, 0, None

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
            addButton = Button(text=' ')

            def addButtonCallback(button):
                addSpecialistDayPeriodMeetingAtGroupAndLocal(specialist, day, period, hiddenGroupSelections[specialist][day][period], hiddenLocalSelections[specialist][day][period])
                hide_widget(addButton, True)
                hide_widget(groupDropdowns[specialist][day][period], False)
                hide_widget(localDropdowns[specialist][day][period], False)
                hide_widget(deleteButtons[specialist][day][period], False)

            addButton.bind(on_release=addButtonCallback)

            addButtons[specialist][day][period] = addButton

            return addButton

        def createGroupDropdown(specialist, day, period):
            dropdown = DropDown()
            for group in classInstance.groups:
                groupButton = Button(text=group.name, size_hint_y=None, height=44)
                groupButton.solverGroup = group

                def groupButtonCallback(button):
                    group = button.solverGroup
                    changeSpecialistDayPeriodGroup(specialist, day, period, hiddenLocalSelections[specialist][day][period], hiddenGroupSelections[specialist][day][period], group.id)
                    hiddenGroupSelections[specialist][day][period] = group.id
                    dropdown.select(group)

                groupButton.bind(on_release=groupButtonCallback)
                dropdown.add_widget(groupButton)

            dropdownButton = Button(text=classInstance.groups[0].name)
            dropdownButton.bind(on_release=lambda instance: dropdown.open(instance))
            dropdown.bind(on_select=lambda instance, group: setattr(dropdownButton, 'text', group.name))
            dropdownButton.size=(300, dropdownButton.size[1])

            groupDropdowns[specialist][day][period] = dropdownButton
            hiddenGroupSelections[specialist][day][period] = 0
            hide_widget(dropdownButton, True)

            return dropdownButton

        def createLocalDropdown(specialist, day, period):
            dropdown = DropDown()
            for local in classInstance.locals:
                localButton = Button(text=local.name, size_hint_y=None, height=44)
                localButton.solverLocal = local

                def localButtonCallback(button):
                    local = button.solverLocal
                    changeSpecialistDayPeriodLocal(specialist, day, period, hiddenGroupSelections[specialist][day][period], hiddenLocalSelections[specialist][day][period], local.id)
                    hiddenLocalSelections[specialist][day][period] = local.id
                    dropdown.select(local)
                
                localButton.bind(on_release=localButtonCallback)
                dropdown.add_widget(localButton)

            dropdownButton = Button(text=classInstance.locals[0].name)
            dropdownButton.bind(on_release=lambda instance: dropdown.open(instance))
            dropdown.bind(on_select=lambda instance, local: setattr(dropdownButton, 'text', local.name))
            dropdownButton.size=(300, dropdownButton.size[1])

            localDropdowns[specialist][day][period] = dropdownButton
            hiddenLocalSelections[specialist][day][period] = 0
            hide_widget(dropdownButton, True)

            return dropdownButton

        def createDeleteMeetingButton(specialist, day, period):
            deleteButton = Button(text='X')

            def deleteButtonCallback(button):
                removeSpecialistDayPeriodMeeting(specialist, day, period)

                hide_widget(addButtons[specialist][day][period], False)
                hide_widget(groupDropdowns[specialist][day][period], True)
                hide_widget(localDropdowns[specialist][day][period], True)
                hide_widget(deleteButton, True)

            deleteButton.bind(on_release=deleteButtonCallback)
            deleteButton.size=(30, deleteButton.size[1])

            deleteButtons[specialist][day][period] = deleteButton
            hide_widget(deleteButton, True)

            return deleteButton

        def createCell(specialist, day, period):
            cellLayout = BoxLayout()
            cellLayout.add_widget(createAddMeetingButton(specialist, day, period))
            cellLayout.add_widget(createGroupDropdown(specialist, day, period))
            cellLayout.add_widget(createLocalDropdown(specialist, day, period))
            cellLayout.add_widget(createDeleteMeetingButton(specialist, day, period))
            return cellLayout

        rootGrid = GridLayout(cols=classInstance.school.daysInCycle + 1, rows=len(classInstance.specialists)*classInstance.school.periodsInDay + classInstance.school.periodsInDay, size_hint=(None, None), size=(2000, 1000))
        rootGrid.bind(minimum_height=rootGrid.setter('height'))
        rootGrid.bind(minimum_width=rootGrid.setter('width'))

        rootGrid.add_widget(Label())
        for cycleDay in range(classInstance.school.daysInCycle):
            dayLabel = Label(text=str(cycleDay + 1))
            dayLabel.size = dayLabel.texture_size
            rootGrid.add_widget(dayLabel)

        for period in range(classInstance.school.periodsInDay):
            for specialist in classInstance.specialists:
                specialistLabel = Label(text=specialist.name)
                specialistLabel.size = specialistLabel.texture_size
                rootGrid.add_widget(specialistLabel)
                for day in range(classInstance.school.daysInCycle):
                    rootGrid.add_widget(createCell(specialist.id, day, period))
            if period != classInstance.school.periodsInDay - 1:
                for day in range(classInstance.school.daysInCycle + 1):
                    rootGrid.add_widget(Label())

        rootScrollViewer = ScrollView(size_hint=(None, None), size=(Window.width, Window.height))
        Window.bind(on_resize=lambda window, x, y: setattr(rootScrollViewer, 'size', (x, y)))
        rootScrollViewer.add_widget(rootGrid)
        return rootScrollViewer