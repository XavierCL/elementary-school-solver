from problemInstances import classes2
import solver.solutionInstance as solutionInstance

import numpy as np

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
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

def setHiddenAttr(wid, attrName, value):
    if hasattr(wid, 'saved_hide_attrs'):
        height, size_hint_y, opacity, disabled, width, size_hint_x = wid.saved_hide_attrs
        if attrName == 'height':
            height = value
        elif attrName == 'size_hint_y':
            size_hint_y = value
        elif attrName == 'opacity':
            opacity = value
        elif attrName == 'disabled':
            disabled = value
        elif attrName == 'width':
            width = value
        elif attrName == 'size_hint_x':
            size_hint_x = value
        else:
            setattr(wid, attrName, value)
        wid.saved_hide_attrs = height, size_hint_y, opacity, disabled, width, size_hint_x
    else:
        setattr(wid, attrName, value)

class TutorialApp(App):
    def build(self):

        # todo: Import json from a button
        classInstance = classes2.classes2()

        # todo: Import json from a button
        self.lastSolution = solutionInstance.SolutionInstance(classInstance, np.zeros((len(classInstance.groups), len(classInstance.specialists), len(classInstance.locals), classInstance.school.daysInCycle, classInstance.school.periodsInDay)).astype(np.bool))

        # todo: make classes and resources modifiable through UI and exportable
        # todo: make soft constraint editable throught the UI, and savable
        # todo: make hard constraint opt-out using checkboxes

        # todo make solver runnable on the last solution

        rootGrid = RelativeLayout(size_hint=(None, None))

        for cycleDay in range(classInstance.school.daysInCycle):
            dayLabel = Label(text=str(cycleDay + 1), pos=(cycleDay*100+100, 100))
            dayLabel.size = (100, 44)
            rootGrid.add_widget(dayLabel)

        btn = Button(text ='Hello world',
                 pos=(396.0, 298.0),
                 size_hint=(None, None))
        btn.bind(texture_size=lambda instance, s: setattr(btn, 'size', (s[0] + 10, s[1] + 10)))
        btn1 = Button(text ='Hello world !!!!!!!!!',
                 pos=(137.33, 298.0),
                 size_hint=(None, None))
        btn1.bind(texture_size=lambda instance,s: setattr(btn1, 'size', s))
  
        # adding widget i.e button  
        rootGrid.add_widget(btn)
        rootGrid.add_widget(btn1)

        maxX = 0
        maxY = 0
        for child in rootGrid.children:
            maxX = child.width + child.x if child.width + child.x > maxX else maxX
            maxY = child.height + child.y if child.height + child.y > maxY else maxY
        
        rootGrid.size = (maxX, maxY)

        rootScrollViewer = ScrollView(size_hint=(None, None), size=(Window.width, Window.height))
        Window.bind(on_resize=lambda window, x, y: setattr(rootScrollViewer, 'size', (x, y)))
        rootScrollViewer.add_widget(rootGrid)
        return rootScrollViewer