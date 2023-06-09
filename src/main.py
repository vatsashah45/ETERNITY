from typing import Callable

import sys
import os
import re 

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from Interpreter import Interpreter

# Colours used by the app.
COLOR_DARK     = '#191919'
COLOR_MEDIUM   = '#353535'
COLOR_MEDLIGHT = '#5A5A5A'
COLOR_LIGHT    = '#DDDDDD'
COLOR_ACCENT   = '#10a1a1'
COLOR_WRONG    = '#ff0000'

def helpStr() -> str:
    '''Returns the string for help documentation'''

    helpStr = '''<b>ETERNITY has the following functions and the proper syntax for each of them:</b><br>
    <b>Numbers:</b> Numbers can be written as 0.123, .123, 123. And can be joined together with irrational constants like 𝛑 and e, 3𝛑, 3e. Euler’s number e does not have to be raised to an exponent. The default value for e is e^1.<br>
    <b>Addition:</b> x+y. Simple addition operator. Requires two arguments, one on each side of the plus operator.<br>
    <b>Subtraction:</b> x-y. Simple subtraction operator. Requires two arguments, one on each side of the minus operator.<br>
    <b>Multiplication:</b> x*y. Requires two arguments, one on each side of the multiplication symbol. Parenthesis can extend an argument.<br>
    <b>Division:</b> x/y. Requires two arguments, one on each side of the division symbol. Parentheses can extend an argument, but division takes one numerator and one denominator. <br>
    <b>Trig:</b> (sin(x), arccos(x), tanh(x)). Every trigonometry function requires one argument. The arguments can be lengthy expressions with other functions.<br>
    <b>Log:</b> logb(a).Calculates the logarithm of a base b to an argument a. Requires two arguments. Parentheses can be used for long expressions for the base or argument.<br>
    <b>Exponent:</b> (x^y). Applies a base x to the power of exponent y. x is multiplied by itself y times. x and y can be decimal numbers. Parentheses can be used for both the base and the exponent.<br>
    <b>Factorial:</b> (x)!. Returns the argument multiplied by each integer before it until 1. Argument must be an integer greater than or equal to 0. Factorial will take the number just before it. Can also use parentheses.<br>
    <b>Standard Deviation:</b> σ([x]). Statistic to observe how spread out the data is. Requires a list. If no list is present, it will return 0. A syntactically correct list requires values separated by commas, inside square brackets ([]). An example of proper syntax: [6, 8, 10]. <br>
    <b>Gamma:</b> Γ(x). Extension of the factorial function to complex numbers (Ex: 9 + 5i). Requires one argument. The gamma function will take the first number if no parenthesis are present. Parentheses can extend the length of the argument for the Gamma function.<br>
    <b>MAD:</b> MAD([x]). Calculates how far on average each data point is from their mean. Requires a list. If no list is present, it will return 0. A syntactically correct list requires values separated by commas, inside square brackets ([]). An example of proper syntax: [6, 8, 10].<br>
    <b>Square Root:</b>√(x). The square root finds the number at which when multiplied by itself gives you the inputted argument x. Requires one argument. Square Root will take the first number if no parentheses are present. Parentheses can extend the length of the square root.<br>
    Parentheses are another very important operator. They act like multiplication when there are two sets of parentheses side by side.They also help guide the order of operations and keep them succinct. <br>
    When in doubt, use parentheses!'''

    return helpStr

def aboutStr() -> str:
    '''Returns the string for the About page.'''
    aboutStr = '''Welcome to the ETERNITY calculator!<br>
    This calculator was programmed for those scientific enthusiasts and simple minded people alike. We were looking to bring users requiring difficult math functions as well as users needing only simple operations.<br>
    The ETERNITY calculator provides the ability to swap between a light theme and a dark theme, and offers the choice between degrees or radians for trigonometry functions. The functions are very intuitive if you have seen them before, if not there is a help page which provides descriptions of every single button with their proper syntax.<br>
    This calculator was made for class COMP-354 at concordia, with the collaboration of the following students: Danny Roux-Dufault, Nicholas Simo, Arash Singh, Vatsa Kartik Shah, William Robinson, Tyler Shanks, and Andrei Serban.<br>
    Enjoy!
    '''
    return aboutStr

class CustomListViewItem(QWidget):
    '''Custom List View Item widget to display one equation, its result, and '''

    #custom Qt signal to signalize to the List View that this item needs to be removed
    deleteme = pyqtSignal(QListWidgetItem)

    def __init__(self, equation: str, result: str, parent: QListWidget, listItem: QListWidgetItem) -> None:
        '''Constructor of the Custom Item, setup the UI elements'''
        super(CustomListViewItem, self).__init__(parent=parent)

        # Save the List Item that this widget belongs to
        self.listItem = listItem

        # Create the equation label
        self.equationText = QLabel(self)
        self.equationText.setText(equation)
        self.equationText.setSizePolicy(parent.sizePolicy())
        self.equationText.setAlignment(Qt.AlignRight)
        self.equationText.setStyleSheet('border: 1px solid ' + COLOR_MEDLIGHT)
        self.equationText.setTextFormat(Qt.RichText)

        # Create the X button used to delete this item
        self.deleteButton = QPushButton('X', self)
        self.deleteButton.pressed.connect(self.__deleteButtonPressed)

        # Create the label used to display the answer of the equation
        self.answerLabel = QLabel(result, self)

        # Create the layout of the widgets
        self.hBox = QHBoxLayout()
        self.hBox.addWidget(self.deleteButton)
        self.hBox.addStretch()
        self.hBox.addWidget(self.answerLabel)

        self.vBox = QVBoxLayout()
        self.vBox.addWidget(self.equationText)
        self.vBox.addItem(self.hBox)

        self.setLayout(self.vBox)

    def __deleteButtonPressed(self):
        '''Signal to the List View that this item needs to be deleted'''
        self.deleteme.emit(self.listItem)

class HistoryWindow(QWidget):
    '''Window that shows the history of the equations, and their results'''

    # Custom signal to signalize to the Main Window that an equation needs to be set
    setEquationText = pyqtSignal(str)

    def __init__(self, parent: QWidget) -> None:
        '''Constructor of the History Window, setup the UI elements'''
        super(HistoryWindow, self).__init__()
        
        # Set window information
        self.setWindowTitle('ETERNITY History')
        self.setMinimumSize(450, 300)
        self.setSizePolicy(parent.sizePolicy())

        # Keep track of the equations in a list
        self.equationList = []

        # Restore the geometry of the History window from the settings
        settings = QSettings()
        self.restoreGeometry(settings.value('HistoryWindow/geometry', QByteArray()))

        # Get back the list of previous equations saved from the settings
        size = settings.beginReadArray('HistoryEquations')
        for i in range(size):
            settings.setArrayIndex(i)
            equation = settings.value('equation')
            answer = settings.value('answer')
            self.equationList.insert(0, (equation, answer))

        # Simple description label
        label = QLabel('History:')
        label.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)

        # Create the List View that will hold the History of equations
        self.listView = QListWidget(self)
        self.listView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.listView.itemClicked.connect(self.itemClicked)

        # Create the button to clear all equations
        self.clearAllButton = QPushButton('Clear All', self)
        self.clearAllButton.pressed.connect(self.__clearAllPressed)

        # Make the clear all button show on the right side of the window
        self.hBox = QHBoxLayout()
        self.hBox.addStretch()
        self.hBox.addWidget(self.clearAllButton)

        # Add all widgets to the Window
        self.vBox = QVBoxLayout()
        self.vBox.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.vBox.addWidget(label)
        self.vBox.addWidget(self.listView)
        self.vBox.addItem(self.hBox)

        self.setLayout(self.vBox)

        # Add the equations back to the list view
        for item in reversed(self.equationList):
            self.createNewListItem(item[0], item[1])

    def closeEvent(self, ev: QCloseEvent) -> None:
        '''
            Function called when the History Window closes.
            Handles what needs to be saved before closing the window.
        '''

        settings = QSettings()
        
        # Save the geometry of the window (size, position)
        settings.setValue('HistoryWindow/geometry', self.saveGeometry())

        # Save the history of equations.
        settings.beginWriteArray('HistoryEquations')
        for i in range(len(self.equationList)):
            settings.setArrayIndex(i)
            settings.setValue('equation', self.equationList[i][0])
            settings.setValue('answer', self.equationList[i][1])
        settings.endArray()

        # Continue the save event
        super().closeEvent(ev)

    def __clearAllPressed(self) -> None:
        '''
            Function called when the Clear All button is pressed.
            Clears all the equations from the list.    
        '''
        self.listView.clear()
        self.equationList.clear()

    @pyqtSlot(QListWidgetItem)
    def removeItem(self, item: QListWidgetItem) -> None:
        '''Function called to handle when an item from the List View is to be removed'''
        row = self.listView.row(item)
        self.listView.takeItem(row)
        self.equationList.pop(row)

    def addEquation(self, equation: str, answer: str) -> None:
        '''Function called to add a new equation to the List'''
        self.createNewListItem(equation, answer)
        self.equationList.insert(0, (equation, answer))

    def createNewListItem(self, equation: str, answer: str) -> None:
        '''Function called to create a new List View Item'''

        # Create an item
        listViewItem = QListWidgetItem()
        listViewItem.setFlags(Qt.ItemFlag.NoItemFlags)

        # Create the custom list view item
        itemWidget = CustomListViewItem(equation, answer, self.listView, listViewItem)
        itemWidget.deleteme.connect(self.removeItem)

        listViewItem.setSizeHint(itemWidget.sizeHint())

        # Insert the item
        self.listView.insertItem(0, listViewItem)
        
        # Set the widget of the item to the custom list view item
        self.listView.setItemWidget(listViewItem, itemWidget)

    def itemClicked(self, item: QListWidgetItem) -> None:
        '''Function called when an item is clicked. Send the equation to the MainWindow to be displayed'''
        # Get the row that was clicked
        row = self.listView.row(item)

        # Get the corresponding equation
        equation = self.equationList[row][0]

        # Send the equation to the MainWindow
        self.setEquationText.emit(equation)

class ArrayInputDialog(QDialog):
    '''Custom Dialog to input a comma separated array of numbers'''
    def __init__(self, title : str, text : str, parent : QWidget = None) -> None:
        '''Constructor of the custom dialog, setup UI elements'''
        super(ArrayInputDialog, self).__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose)
        self.setWindowTitle(title)

        # match any string composed of comma separated integer of float numbers 
        self.regExVal = QRegExpValidator(QRegExp(r'^(\s*(\d+.\d+|\d+)\,\s*)*(\d+.\d+|\d+)$'))

        # Create the line to input the array of numbers
        self.lineEdit = QLineEdit(self)
        self.lineEdit.textChanged.connect(self.validateText)
        self.lineEdit.setValidator(self.regExVal)

        # Create the buttons to interact with the dialog
        self.buttonBox = QDialogButtonBox(self)
        self.okButton = self.buttonBox.addButton('Ok', QDialogButtonBox.ButtonRole.AcceptRole)
        self.cancelButton = self.buttonBox.addButton('Cancel', QDialogButtonBox.ButtonRole.RejectRole)

        # Add the widgets to the dialog
        self.vBox = QVBoxLayout()
        self.vBox.addWidget(QLabel(self.tr(text)))
        self.vBox.addWidget(self.lineEdit)
        self.vBox.addWidget(self.buttonBox)
        self.setLayout(self.vBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.validateText('')

    def validateText(self, newStr : str) -> None:
        '''Function called whenever the value of the line edit changes. Validates that the input is valid.'''

        if self.regExVal.validate(newStr, 0)[0] == QValidator.State.Acceptable:
            self.lineEdit.setStyleSheet('border: 1px solid ' + COLOR_MEDLIGHT)
            self.okButton.setDisabled(False)
        else:
            self.lineEdit.setStyleSheet('border: 1px solid ' + COLOR_WRONG)
            self.okButton.setDisabled(True)
        
    def getValue(self) -> str:
        '''Returns the value entered by the user'''
        return self.lineEdit.text()

class PushButton(QPushButton):
    '''Custom Push Button to display Rich Text'''
    def __init__(self, parent=None, text=None) -> None:
        if parent is not None:
            super().__init__(parent)
        else:
            super().__init__()
        
        self.__lbl = QLabel(self)
        if text is not None:
            self.__lbl.setText(text)
        
        # Create the rich text label
        self.__lyt = QHBoxLayout()
        self.__lyt.setContentsMargins(0, 0, 0, 0)
        self.__lyt.setSpacing(0)
        self.setLayout(self.__lyt)
        self.__lbl.setAttribute(Qt.WA_TranslucentBackground)
        self.__lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.__lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.__lbl.setTextFormat(Qt.RichText)
        self.__lbl.setAlignment(Qt.AlignCenter)
        self.__lyt.addWidget(self.__lbl)

    def setText(self, text) -> None:
        '''Overwritten function to set the text of the button'''
        self.__lbl.setText(text)
        self.updateGeometry()

    def sizeHint(self) -> QSize:
        '''Overwritten function to get the size hint of the button'''
        s = QPushButton.sizeHint(self)
        w = self.__lbl.sizeHint()
        s.setWidth(w.width())
        s.setHeight(w.height())
        return s

class MainWindow(QMainWindow):
    '''Main Window of the application'''

    def __init__(self, app, parent=None) -> None:
        '''Constructor of the Main Window. Setup UI elements'''
        super(MainWindow, self).__init__(parent)

        # Variables used by the equation text line edit
        self.cursorPosition = 0
        self.equationString = ''
        self.isDegree = False
    
        self.app = app
    
        # Create the history window 
        self.history = HistoryWindow(self)
        self.history.setEquationText.connect(self.setEquationText)

        settings = QSettings()
        self.restoreGeometry(settings.value('geometry', QByteArray()))
        self.restoreState(settings.value('state', QByteArray()))

        # Get the light and dark mode stylesheet
        self.lightStylesheet = self.app.styleSheet()
        darkStylesheetFile = QFile('darkstyle.qss')
        darkStylesheetFile.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(darkStylesheetFile)
        self.darkStylesheet = stream.readAll()
        
        # Set the style to the previous setting
        if str(settings.value('AppStyle')) == 'light':
            self.app.setStyleSheet(self.lightStylesheet)
        else:
            self.app.setStyleSheet(self.darkStylesheet)

        # Set the minimum window size possible
        self.setMinimumSize(450, 500)
        
        # Create the Layout
        self.mainLayout = QGridLayout()
        self.mainLayout.setObjectName('mainLayout')
        self.mainLayoutWidget = QWidget(self)
        self.mainLayoutWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainLayoutWidget)
        
        # Create the MenuBar
        self.menuBar = QMenuBar(self)

        self.helpMenu = QMenu('H&elp', self.menuBar)
        aboutAction = self.helpMenu.addAction('&About')
        aboutAction.triggered.connect(self.__onAboutActionTriggered)
        helpAction = self.helpMenu.addAction('&Help')
        helpAction.triggered.connect(self.__onHelpActionTriggered)
        
        self.styleMenu = QMenu('&Style', self.menuBar)
        lightStyleAction = self.styleMenu.addAction('&Light')
        lightStyleAction.triggered.connect(self.__onLightStyleActionTriggered)
        darkStyleAction = self.styleMenu.addAction('&Dark')
        darkStyleAction.triggered.connect(self.__onDarkStyleActionTriggered)

        self.menuBar.addMenu(self.styleMenu)
        self.menuBar.addMenu(self.helpMenu)

        historyAction = self.menuBar.addAction('&History')
        historyAction.triggered.connect(self.__onHistoryActionTriggered)

        self.mainLayout.setMenuBar(self.menuBar)
        
        # Create the UI elements
        self.sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Row 0
        row = 0
        self.equationText = QLabel(self)
        self.equationText.setText('_')
        self.equationText.setSizePolicy(self.sizePolicy)
        self.equationText.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.equationText.setStyleSheet('border: 1px solid ' + COLOR_MEDLIGHT)
        self.equationText.setTextFormat(Qt.RichText)
        self.mainLayout.addWidget(self.equationText, row, 0, 1, 5)
        row += 1
        
        # Row 1
        self.errorMessageLabel = QLabel(self)
        self.errorMessageLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.mainLayout.addWidget(self.errorMessageLabel, row, 0, 1, 4)
        self.degButton = self.__addButton('RAD', 'DegRad', '', row, 4, slot=self.switchDegRad)
        row += 1

        # Create the buttons
        # Row 2
        self.__addButton('&lt;&lt;', 'leftButton', '', row, 0, slot=self.cursorLeft, shortcut=QKeySequence(Qt.Key_Left))
        self.__addButton('&gt;&gt;', 'rightButton', '', row, 1, slot=self.cursorRight, shortcut=QKeySequence(Qt.Key_Right))
        self.__addButton(u'\u2190', 'backButton', '<-', row, 2, slot=self.backspace, shortcut=QKeySequence(Qt.Key_Backspace))
        self.__addButton('Del', 'deleteButton', '->', row, 3, slot=self.delete, shortcut=QKeySequence(Qt.Key_Delete))
        self.__addButton('AC', 'clearButton', 'AC', row, 4, slot=self.clearText)
        row += 1
        
        # Row 3 
        self.__addButton(u'\U0001D745', 'piButton', u'\U0001D745', row, 0)
        self.__addButton('<i>e</i>', 'eButton', 'e', row, 1, shortcut=QKeySequence('e'))
        self.__addButton('x<sup>2</sup>', 'squareButton', '^2', row, 2)
        self.__addButton('x<sup>3</sup>', 'cubeButton', '^3', row, 3)
        self.__addButton('x<sup>y</sup>', 'expoButton', '^', row, 4, shortcut=QKeySequence('^'))
        row += 1
        
        # Row 4
        self.__addButton('sin(x)', 'sinButton', 'sin()', row, 0)
        self.__addButton('cos(x)', 'cosButton', 'cos()', row, 1)
        self.__addButton('tan(x)', 'tanButton', 'tan()', row, 2)
        self.__addButton('x!', 'factButton', '!', row, 3, shortcut=QKeySequence('!'))
        self.__addButton(u'\u221a', 'sqrtButton', u'\u221a()', row, 4)
        row += 1

        # Row 5
        self.__addButton('sin<sup>-1</sup>(x)', 'arcsinButton', 'arcsin()', row, 0)
        self.__addButton('cos<sup>-1</sup>(x)', 'arccosButton', 'arccos()', row, 1)
        self.__addButton('tan<sup>-1</sup>(x)', 'arctanButton', 'arctan()', row, 2)
        self.__addButton('log<sub>b</sub>(x)', 'logButton', 'log()', row, 3)
        self.__addButton(u'\u0393(x)', 'gammaButton', u'\u0393()', row, 4)
        row += 1

        # Row 6
        self.__addButton('sinh(x)', 'sinhButton', 'sinh()', row, 0)
        self.__addButton('cosh(x)', 'coshButton', 'cosh()', row, 1)
        self.__addButton('tanh(x)', 'tanhButton', 'tanh()', row, 2)
        self.__addButton('MAD(x)',  'madButton', 'MAD()', row, 3, slot = lambda: self.addArrayFunctionToEquation('MAD'))
        self.__addButton(u'\u03c3(x)', 'stddevButton', u'\u03c3()', row, 4, slot = lambda: self.addArrayFunctionToEquation('\u03c3'))
        row += 1
        
        # Row 7
        self.vSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.mainLayout.addItem(self.vSpacer, row, 0, 1, 5)
        row += 1
                
        # Row 8
        self.__addButton('1', 'oneButton', '1', row, 0, shortcut=QKeySequence('1'))
        self.__addButton('2', 'twoButton', '2', row, 1, shortcut=QKeySequence('2'))
        self.__addButton('3', 'threeButton', '3', row, 2, shortcut=QKeySequence('3'))
        self.__addButton('(', 'leftParButton', '(', row, 3, shortcut=QKeySequence('('))
        self.__addButton(')', 'rightParButton', ')', row, 4, shortcut=QKeySequence(')'))
        row += 1

        # Row 9
        self.__addButton('4', 'fourButton', '4', row, 0, shortcut=QKeySequence('4'))
        self.__addButton('5', 'fiveButton', '5', row, 1, shortcut=QKeySequence('5'))
        self.__addButton('6', 'sixButton', '6', row, 2, shortcut=QKeySequence('6'))
        self.__addButton(u'\u00d7', 'multButton', '*', row, 3, shortcut=QKeySequence('*'))
        self.__addButton(u'\u00f7', 'divButton', '/', row, 4, shortcut=QKeySequence('/'))
        row += 1

        # Row 10
        self.__addButton('7', 'sevenButton', '7', row, 0, shortcut=QKeySequence('7'))
        self.__addButton('8', 'eightButton', '8', row, 1, shortcut=QKeySequence('8'))
        self.__addButton('9', 'nineButton', '9', row, 2, shortcut=QKeySequence('9'))
        self.__addButton('+', 'plusButton', '+', row, 3, shortcut=QKeySequence('+'))
        self.__addButton('-', 'minusButton', '-', row, 4, shortcut=QKeySequence('-'))
        row += 1

        # Row 11
        self.__addButton('0', 'zeroButton', '0', row, 0, shortcut=QKeySequence('0'))
        self.__addButton('.', 'dotButton', '.', row, 1, shortcut=QKeySequence('.'))
        self.__addButton('+/-', 'plusminusButton', '-', row, 2)
        self.equalButton = self.__addButton('=', 'equalButton', '=', row, 3, 1, 2, slot=self.compute, shortcut=QKeySequence('='))
        row += 1
      
    def closeEvent(self, ev: QCloseEvent) -> None:
        '''
            Function called when the Main Window closes.
            Handles what needs to be saved before closing the window.
        '''
        # Close the history window
        self.history.close()

        settings = QSettings()
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('state', self.saveState())
        
        super().closeEvent(ev)

    def __addButton(self, text: str, name: str, equation: str, row: int, col: int, rowSpan: int = 1, colSpan: int = 1, slot: Callable = None, shortcut: QKeySequence = None) -> QPushButton:
        '''Function called to add a button to the layout. Returns the created button'''
        # Create the button widget
        newButton = PushButton(self, text)
        newButton.setObjectName(name)
        newButton.setSizePolicy(self.sizePolicy)
        
        # If a function is not passed as the action, create a defaut action of what to do
        if slot == None:
            slot = lambda: self.addTextToEquation(equation)
        
        # Attach the function to when the button is pressed
        newButton.pressed.connect(slot)
        
        # If a shortcut is set, assign it to the button
        if shortcut != None:
            newButton.setShortcut(shortcut)
        
        # Add the button to the given position in the layout
        self.mainLayout.addWidget(newButton, row, col, rowSpan, colSpan)
        
        return newButton
      
    def __onAboutActionTriggered(self) -> None:
        '''Action when the menu->about is clicked.'''

        # Create a message box with the about information
        tmpFont = self.app.font()
        tmpFont.setPixelSize(12)

        msb = QMessageBox(self)
        msb.setWindowTitle('About')
        msb.setText(aboutStr())
        msb.setFont(tmpFont)
        msb.setStandardButtons(QMessageBox.Ok)
        msb.exec_()
        
    def __onHelpActionTriggered(self) -> None:
        '''Action when the menu->help is clicked.'''
        
        # Create a message box with the help information
        tmpFont = self.app.font()
        tmpFont.setPixelSize(12)

        msb = QMessageBox(self)
        msb.setWindowTitle('Help')
        msb.setText(helpStr())
        msb.setFont(tmpFont)
        msb.setFixedWidth(1000)
        msb.setStandardButtons(QMessageBox.Ok)
        
        msb.exec_()
        
    def __onLightStyleActionTriggered(self) -> None:
        '''Function called when the light style menu item is clicked'''
        self.app.setStyleSheet(self.lightStylesheet)
        settings = QSettings()
        settings.setValue('AppStyle', 'light')

    def __onDarkStyleActionTriggered(self) -> None:
        '''Function called when the dark style menu item is clicked'''
        self.app.setStyleSheet(self.darkStylesheet)
        settings = QSettings()
        settings.setValue('AppStyle', 'dark')
    
    def __onHistoryActionTriggered(self) -> None:
        '''Function called when the history menu item is clicked'''
        self.history.show()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        '''Overwritten function to handle the mouse press event'''
        # ignore mouse presses on the main window itself so that focus is not lost
        event.ignore()

    def validateEquation(self) -> None:
        '''Function called to check wether the equation is valid or not'''
        valid, error = Interpreter(self.equationString).isValid()
        if valid:
            self.equationText.setStyleSheet('border: 1px solid ' + COLOR_MEDLIGHT)
            self.equalButton.setEnabled(True)
        else:
            self.equationText.setStyleSheet('border: 1px solid ' + COLOR_WRONG)
            self.equalButton.setEnabled(False)
      
    def addTextToEquation(self, functionStr: str) -> None:
        '''Function called to add element to the equation'''

        # Add the string to the current location of the cursor
        self.equationString = self.equationString[:self.cursorPosition] + functionStr + self.equationString[self.cursorPosition:]
        
        # Calculate the new cursor position
        self.cursorPosition += len(functionStr)
        
        # If the parameter is a function, sets the cursor to inside the parenthesis
        if len(functionStr) > 1 and functionStr[-1] == ')' and functionStr[-2] != ']':
            self.cursorPosition -= 1
        
        # Update the equation shown
        self.writeEquation()

    def addArrayFunctionToEquation(self, functionStr: str) -> None:
        '''Function called to ask the user to input an array of numbers to the equation'''
        arrayInput = ArrayInputDialog('Input values', 'Enter a list of numbers, separated by commas:', self)
        if arrayInput.exec():
            arrayInputValues = arrayInput.getValue().strip()
            self.addTextToEquation(functionStr + '([' + arrayInputValues + '])')

    def switchDegRad(self) -> None:
        '''
            Function called when the "degree" button is called.
            Switches the mode between degree and radian
        '''
        if self.isDegree:
            self.degButton.setText('RAD')
        else:
            self.degButton.setText('DEG')
        self.isDegree = not self.isDegree

    def cursorLeft(self) -> None:
        '''Function called to move the cursor 1 step to the left'''
        self.cursorPosition -= 1
        if self.cursorPosition < 0:
            self.cursorPosition = 0
        self.writeEquation()
      
    def cursorRight(self) -> None:
        '''Function called to move the cursor 1 step to the right'''
        self.cursorPosition += 1
        if self.cursorPosition > len(self.equationString):
            self.cursorPosition = len(self.equationString)
        self.writeEquation()
    
    def writeEquation(self) -> None:
        '''Function called to write the equation to the label, adding the cursor to the correct location'''
        # Remove error message
        self.errorMessageLabel.setText('')

        # write a _ character under the cursor position
        if self.cursorPosition == len(self.equationString):
            tmpStr = self.equationString + '_'
        else:
            tmpStr = self.equationString[:self.cursorPosition] + '<u>' + self.equationString[self.cursorPosition] + '</u>' + self.equationString[self.cursorPosition+1:]

        self.equationText.setText(tmpStr)
        self.validateEquation()
      
    def backspace(self) -> None:
        '''
            Function called when the backspace button is pressed.
            Remove the character before the cursor position
        '''
        back = self.cursorPosition - 1
        if back < 0:
            back = 0
        self.equationString = self.equationString[:back] + self.equationString[self.cursorPosition:]
        self.cursorLeft()
        self.writeEquation()
      
    def delete(self) -> None:
        '''
            Function called when the delete button is pressed.
            Remove the character on the cursor position
        '''
        front = self.cursorPosition + 1
        if front > len(self.equationString):
            front = len(self.equationString)
        self.equationString = self.equationString[:self.cursorPosition] + self.equationString[front:]
        self.writeEquation()

    def clearText(self) -> None:
        '''Function called to clear the equation'''
        self.equationText.setText('_')
        self.equationString = ''
        self.cursorPosition = 0
      
    def compute(self) -> None:
        '''Function called to get the answer of the equation, displaying the errors if any'''
        answer, valid, error = Interpreter(self.equationString).evaluateEquation(self.isDegree)
        if valid:
            self.history.addEquation(self.equationString, str(answer))
            self.clearText()
            self.addTextToEquation(str(answer))
        else:
            self.errorMessageLabel.setText(error)

    def setEquationText(self, equation: str) -> None:
        '''Set the text of the equation'''
        self.clearText()
        self.addTextToEquation(equation)
        
def main(argv) -> None:

    # Create the QT app
    app = QApplication(argv)
    app.setOrganizationName('comp354')
    app.setApplicationName('ETERNITY')

    # Increase the font size
    font = app.font()
    font.setPixelSize(22)
    app.setFont(font)
    
    # Create the main window
    window = MainWindow(app)
    window.setWindowTitle('ETERNITY Calculator')
    window.show()

    # Start the app, returning the error code when the app closes
    sys.exit(app.exec_())


if __name__ == '__main__':
    main(sys.argv)