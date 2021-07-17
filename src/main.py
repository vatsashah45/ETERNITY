from typing import Callable

import sys
import os
import re 

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from FunctionExponent import FunctionExponent

COLOR_DARK     = '#191919'
COLOR_MEDIUM   = '#353535'
COLOR_MEDLIGHT = '#5A5A5A'
COLOR_LIGHT    = '#DDDDDD'
COLOR_ACCENT   = '#10a1a1'
COLOR_WRONG    = '#ff0000'

def helpStr():
    return 'Help String'

class CustomListViewItem(QWidget):

    deleteme = pyqtSignal(QListWidgetItem)

    def __init__(self, equation: str, result: str, parent: QListWidget, listItem: QListWidgetItem) -> None:
        super(CustomListViewItem, self).__init__(parent=parent)

        self.listItem = listItem

        self.equationText = QLabel(self)
        self.equationText.setText(equation)
        self.equationText.setSizePolicy(parent.sizePolicy())
        self.equationText.setAlignment(Qt.AlignRight)
        self.equationText.setStyleSheet('border: 1px solid ' + COLOR_MEDLIGHT)
        self.equationText.setTextFormat(Qt.RichText)

        self.deleteButton = QPushButton('X', self)
        self.deleteButton.pressed.connect(self.__deleteButtonPressed)

        self.answerLabel = QLabel(result, self)

        self.hBox = QHBoxLayout()
        self.hBox.addWidget(self.deleteButton)
        self.hBox.addStretch()
        self.hBox.addWidget(self.answerLabel)

        self.vBox = QVBoxLayout()
        self.vBox.addWidget(self.equationText)
        self.vBox.addItem(self.hBox)

        self.setLayout(self.vBox)

    def __deleteButtonPressed(self):
        self.deleteme.emit(self.listItem)

class HistoryWindow(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super(HistoryWindow, self).__init__()
        
        self.setWindowTitle('ETERNITY History')
        self.setMinimumSize(450, 300)
        self.setSizePolicy(parent.sizePolicy())

        self.listView = QListWidget(self)
        self.listView.setSizePolicy(self.sizePolicy())

        self.clearAllButton = QPushButton('Clear All', self)
        self.clearAllButton.pressed.connect(self.__clearAllPressed)

        self.hBox = QHBoxLayout()
        self.hBox.addStretch()
        self.hBox.addWidget(self.clearAllButton)

        self.vBox = QVBoxLayout()
        self.vBox.addWidget(QLabel('History:'))
        self.vBox.addWidget(self.listView)
        self.vBox.addItem(self.hBox)

        self.setLayout(self.vBox)

    def __clearAllPressed(self):
        self.listView.clear()

    @pyqtSlot(QListWidgetItem)
    def removeItem(self, item: QListWidgetItem):
        print('remove')
        self.listView.takeItem(self.listView.row(item))

    def addEquation(self, equation: str, answer: str):

        listViewItem = QListWidgetItem(self.listView)
        listViewItem.setFlags(Qt.ItemFlag.NoItemFlags)

        itemWidget = CustomListViewItem(equation, answer, self.listView, listViewItem)
        itemWidget.deleteme.connect(self.removeItem)

        listViewItem.setSizeHint(itemWidget.sizeHint())

        self.listView.insertItem(0, listViewItem)
        self.listView.setItemWidget(listViewItem, itemWidget)

class ArrayInputDialog(QDialog):
    def __init__(self, title : str, text : str, parent : QWidget = None) -> None:
        super(ArrayInputDialog, self).__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose)
        self.setWindowTitle(title)

        # match any string composed of comma separated integer of float numbers 
        #self.regEx = r'^(\s*(\d+.\d+|\d+)\,\s*)*(\d+.\d+|\d+)$'
        self.regExVal = QRegExpValidator(QRegExp(r'^(\s*(\d+.\d+|\d+)\,\s*)*(\d+.\d+|\d+)$'))

        self.lineEdit = QLineEdit(self)
        self.lineEdit.textChanged.connect(self.validateText)
        self.lineEdit.setValidator(self.regExVal)

        self.buttonBox = QDialogButtonBox(self)
        self.okButton = self.buttonBox.addButton('Ok', QDialogButtonBox.ButtonRole.AcceptRole)
        self.cancelButton = self.buttonBox.addButton('Cancel', QDialogButtonBox.ButtonRole.RejectRole)

        self.vBox = QVBoxLayout()
        self.vBox.addWidget(QLabel(self.tr(text)))
        self.vBox.addWidget(self.lineEdit)
        self.vBox.addWidget(self.buttonBox)
        self.setLayout(self.vBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.validateText('')

    def validateText(self, newStr : str) -> None:
        if self.regExVal.validate(newStr, 0)[0] == QValidator.State.Acceptable:
            self.lineEdit.setStyleSheet('border: 1px solid ' + COLOR_MEDLIGHT)
            self.okButton.setDisabled(False)
        else:
            self.lineEdit.setStyleSheet('border: 1px solid ' + COLOR_WRONG)
            self.okButton.setDisabled(True)
        
    def getValue(self) -> str:
        return self.lineEdit.text()

class PushButton(QPushButton):
    def __init__(self, parent=None, text=None):
        if parent is not None:
            super().__init__(parent)
        else:
            super().__init__()
        
        self.__lbl = QLabel(self)
        if text is not None:
            self.__lbl.setText(text)
        
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
        return

    def setText(self, text):
        self.__lbl.setText(text)
        self.updateGeometry()
        return

    def sizeHint(self):
        s = QPushButton.sizeHint(self)
        w = self.__lbl.sizeHint()
        s.setWidth(w.width())
        s.setHeight(w.height())
        return s

class MainWindow(QWidget):
    def __init__(self, app, parent=None):
        super(MainWindow, self).__init__(parent)

        self.cursorPosition = 0
        self.equationString = ''
        
        self.app = app
        self.history = HistoryWindow(self)

        # Get the light and dark mode stylesheet
        self.lightStylesheet = self.app.styleSheet()
        darkStylesheetFile = QFile(QFileInfo(os.path.realpath(__file__)).absolutePath() + '/darkstyle.qss')
        darkStylesheetFile.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(darkStylesheetFile)
        self.darkStylesheet = stream.readAll()
        
        # Set the style to the previous setting
        if str(QSettings().value('AppStyle')) == 'light':
            self.app.setStyleSheet(self.lightStylesheet)
        else:
            self.app.setStyleSheet(self.darkStylesheet)

        # Set the minimum window size possible
        self.setMinimumSize(450, 500)
        
        # Create the Layout
        self.mainLayout = QGridLayout(self)
        self.mainLayout.setObjectName('mainLayout')
        self.setLayout(self.mainLayout)
        
        # Create the MenuBar
        self.menuBar = QMenuBar(self)

        self.helpMenu = QMenu('H&elp', self.menuBar)
        aboutAction = self.helpMenu.addAction('&About')
        aboutAction.triggered.connect(self.on_aboutAction_triggered)
        helpAction = self.helpMenu.addAction('&Help')
        helpAction.triggered.connect(self.on_helpAction_triggered)
        
        self.styleMenu = QMenu('&Style', self.menuBar)
        lightStyleAction = self.styleMenu.addAction('&Light')
        lightStyleAction.triggered.connect(self.on_lightStyleAction_triggered)
        darkStyleAction = self.styleMenu.addAction('&Dark')
        darkStyleAction.triggered.connect(self.on_darkStyleAction_triggered)

        self.menuBar.addMenu(self.styleMenu)
        self.menuBar.addMenu(self.helpMenu)

        historyAction = self.menuBar.addAction('&History')
        historyAction.triggered.connect(self.on_historyAction_triggered)

        self.mainLayout.setMenuBar(self.menuBar)
        
        # Create the UI elements
        self.sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Row 0
        self.equationText = QLabel(self)
        self.equationText.setText('_')
        self.equationText.setSizePolicy(self.sizePolicy)
        self.equationText.setAlignment(Qt.AlignRight)
        self.equationText.setStyleSheet('border: 1px solid ' + COLOR_MEDLIGHT)
        self.equationText.setTextFormat(Qt.RichText)
        self.mainLayout.addWidget(self.equationText, 0, 0, 1, 5)
        
        # Create the buttons
        # Row 1
        self.addButton('&lt;&lt;', 'leftButton', '', 1, 0, slot=self.cursorLeft, shortcut=QKeySequence(Qt.Key_Left))
        self.addButton('&gt;&gt;', 'rightButton', '', 1, 1, slot=self.cursorRight, shortcut=QKeySequence(Qt.Key_Right))
        self.addButton(u'\u2190', 'backButton', '<-', 1, 2, slot=self.backspace, shortcut=QKeySequence(Qt.Key_Backspace))
        self.addButton('Del', 'deleteButton', '->', 1, 3, slot=self.delete, shortcut=QKeySequence(Qt.Key_Delete))
        self.addButton('AC', 'clearButton', 'AC', 1, 4, slot=self.clearText)
        
        # Row 2
        self.addButton(u'\u03c0', 'piButton', '\u03c0', 2, 0)
        self.addButton('e', 'eButton', 'e', 2, 1, shortcut=QKeySequence('e'))
        self.addButton('x<sup>2</sup>', 'squareButton', '^2', 2, 2)
        self.addButton('x<sup>3</sup>', 'cubeButton', '^3', 2, 3)
        self.addButton('x<sup>y</sup>', 'expoButton', '^', 2, 4, shortcut=QKeySequence('^'))
        
        # Row 3
        self.addButton('sin(x)', 'sinButton', 'sin()', 3, 0)
        self.addButton('cos(x)', 'cosButton', 'cos()', 3, 1)
        self.addButton('tan(x)', 'tanButton', 'tan()', 3, 2)
        self.addButton('x!', 'factButton', '!', 3, 3, shortcut=QKeySequence('!'))
        self.addButton(u'\u221a', 'Button', 'sqrt()', 3, 4)

        # Row 4
        self.addButton('sin<sup>-1</sup>(x)', 'arcsinButton', 'arcsin()', 4, 0)
        self.addButton('cos<sup>-1</sup>(x)', 'arccosButton', 'arccos()', 4, 1)
        self.addButton('tan<sup>-1</sup>(x)', 'arctanButton', 'arctan()', 4, 2)
        self.addButton('log<sub>b</sub>(x)', 'logButton', 'log()', 4, 3)
        self.addButton(u'\u0393(x)', 'gammaButton', u'\u0393()', 4, 4)

        # Row 5
        self.addButton('sinh(x)', 'sinhButton', 'sinh()', 5, 0)
        self.addButton('cosh(x)', 'coshButton', 'cosh()', 5, 1)
        self.addButton('tanh(x)', 'tanhButton', 'tanh()', 5, 2)
        self.addButton('MAD(x)',  'madButton', 'MAD()', 5, 3, slot = lambda: self.addArrayFunctionToEquation('MAD'))
        self.addButton(u'\u03c3(x)', 'stddevButton', u'\u03c3()', 5, 4, slot = lambda: self.addArrayFunctionToEquation('\u03c3'))
        
        #Row 6
        self.vSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.mainLayout.addItem(self.vSpacer, 6, 0, 1, 5)
                
        self.addButton('1', 'oneButton', '1', 7, 0, shortcut=QKeySequence('1'))
        self.addButton('2', 'twoButton', '2', 7, 1, shortcut=QKeySequence('2'))
        self.addButton('3', 'threeButton', '3', 7, 2, shortcut=QKeySequence('3'))
        self.addButton('4', 'fourButton', '4', 8, 0, shortcut=QKeySequence('4'))
        self.addButton('5', 'fiveButton', '5', 8, 1, shortcut=QKeySequence('5'))
        self.addButton('6', 'sixButton', '6', 8, 2, shortcut=QKeySequence('6'))
        self.addButton('7', 'sevenButton', '7', 9, 0, shortcut=QKeySequence('7'))
        self.addButton('8', 'eightButton', '8', 9, 1, shortcut=QKeySequence('8'))
        self.addButton('9', 'nineButton', '9', 9, 2, shortcut=QKeySequence('9'))
        self.addButton('0', 'zeroButton', '0', 10, 0, shortcut=QKeySequence('0'))
        self.addButton('.', 'dotButton', '.', 10, 1, shortcut=QKeySequence('.'))
        self.addButton('+/-', 'plusminusButton', '-', 10, 2)
        
        self.addButton('(', 'leftParButton', '(', 7, 3, shortcut=QKeySequence('('))
        self.addButton(')', 'rightParButton', ')', 7, 4, shortcut=QKeySequence(')'))
        self.addButton(u'\u00d7', 'multButton', '*', 8, 3, shortcut=QKeySequence('*'))
        self.addButton(u'\u00f7', 'divButton', '/', 8, 4, shortcut=QKeySequence('/'))
        self.addButton('+', 'plusButton', '+', 9, 3, shortcut=QKeySequence('+'))
        self.addButton('-', 'minusButton', '-', 9, 4, shortcut=QKeySequence('-'))
        self.equalButton = self.addButton('=', 'equalButton', '=', 10, 3, 1, 2, slot=self.compute, shortcut=QKeySequence('='))
        
    def closeEvent(self, ev: QCloseEvent) -> None:
        self.history.close()

        

        super().closeEvent(ev)

    # add a button to the layout
    def addButton(self, text: str, name: str, equation: str, row: int, col: int, rowSpan: int = 1, colSpan: int = 1, slot: Callable = None, shortcut: QKeySequence = None):
        
        # create the button object
        newButton = PushButton(self, text)
        newButton.setObjectName(name)
        newButton.setSizePolicy(self.sizePolicy)
        
        # if a function is not passed as the action, create a defaut action of what to do
        if slot == None:
            slot = lambda: self.addTextToEquation(equation)
        
        # attach the function to when the button is pressed
        newButton.pressed.connect(slot)
        
        # if a shortcut is set, assign it to the button
        if shortcut != None:
            newButton.setShortcut(shortcut)
        
        # add the button to the given position in the layout
        self.mainLayout.addWidget(newButton, row, col, rowSpan, colSpan)
        
        return newButton
        
    # menu->about shown
    def on_aboutAction_triggered(self):
        msb = QMessageBox(self)
        msb.setWindowTitle('About')
        msb.setText('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce sollicitudin dui pulvinar ante rutrum pretium et non dolor. Quisque pretium sodales nulla, non dapibus magna mollis quis. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Maecenas id sodales felis. Mauris nec finibus orci, et vehicula sapien. Cras id nibh mauris. Praesent nec ante vel diam molestie dictum ut in augue. Suspendisse consectetur lacus non odio faucibus tempus. Proin quis eros sodales, condimentum leo non, blandit turpis. Nullam suscipit semper malesuada. Donec massa orci, fermentum ac dignissim sit amet, iaculis sed magna. Nulla ullamcorper efficitur dui, sit amet consequat ligula.')
        msb.setStandardButtons(QMessageBox.Ok)
        msb.exec_()
        
    # menu->help shown
    def on_helpAction_triggered(self):
        msb = QMessageBox(self)
        msb.setWindowTitle('Help')
        msb.setText(helpStr())
        msb.setStandardButtons(QMessageBox.Ok)
        msb.exec_()
        
    def on_lightStyleAction_triggered(self):
        self.app.setStyleSheet(self.lightStylesheet)
        settings = QSettings()
        settings.setValue('AppStyle', 'light')

    def on_darkStyleAction_triggered(self):
        self.app.setStyleSheet(self.darkStylesheet)
        settings = QSettings()
        settings.setValue('AppStyle', 'dark')
    
    def on_historyAction_triggered(self):
        self.history.show()

    # handle mouse presses
    def mousePressEvent(self, event: QMouseEvent) -> None:
            # ignore mouse presses on the main window itself so that focus is not lost
            event.ignore()
            return

    # check wether the equation is valid or not
    def validateEquation(self):
    
        #TODO: get whether the equation is valid or not from the equation evaluator
        if False:
            self.equationText.setStyleSheet('border: 1px solid ' + COLOR_WRONG)
            self.equalButton.setEnabled(False)
        else:
            self.equationText.setStyleSheet('border: 1px solid ' + COLOR_MEDLIGHT)
            self.equalButton.setEnabled(True)
        
    # add element to the equation
    def addTextToEquation(self, functionStr: str):

        # add the string to the current location of the cursor
        self.equationString = self.equationString[:self.cursorPosition] + functionStr + self.equationString[self.cursorPosition:]
        
        # calculate the new cursor position
        self.cursorPosition += len(functionStr)
        
        # if the parameter is a function, sets the cursor to inside the parenthesis
        if len(functionStr) > 1 and functionStr[-1] == ')':
            self.cursorPosition -= 1
        
        #update the equation shown
        self.writeEquation()

    def addArrayFunctionToEquation(self, functionStr: str):
        
        #arrayInput = QInputDialog.getText(self, 'Input values', 'Enter a list of numbers, separated by commas:', inputMethodHints=Qt.ImhFormattedNumbersOnly)[0]
        arrayInput = ArrayInputDialog('Input values', 'Enter a list of numbers, separated by commas:', self)
        if arrayInput.exec():
            arrayInputValues = arrayInput.getValue().strip()
            self.addTextToEquation(functionStr + '(' + arrayInputValues + ')')

    # move the cursor 1 step to the left
    def cursorLeft(self):
        self.cursorPosition -= 1
        if self.cursorPosition < 0:
            self.cursorPosition = 0
        self.writeEquation()
        
    # move the cursor 1 step to the right
    def cursorRight(self):
        self.cursorPosition += 1
        if self.cursorPosition > len(self.equationString):
            self.cursorPosition = len(self.equationString)
        self.writeEquation()
    
    # write the equation to the label, adding the cursor to the correct location
    def writeEquation(self):

        # write a _ character under the cursor position
        if self.cursorPosition == len(self.equationString):
            tmpStr = self.equationString + '_'
        else:
            tmpStr = self.equationString[:self.cursorPosition] + '<u>' + self.equationString[self.cursorPosition] + '</u>' + self.equationString[self.cursorPosition+1:]

        self.equationText.setText(tmpStr)
        self.validateEquation()
        
    # remove the character before the cursor position
    def backspace(self):
        back = self.cursorPosition - 1
        if back < 0:
            back = 0
        self.equationString = self.equationString[:back] + self.equationString[self.cursorPosition:]
        self.cursorLeft()
        self.writeEquation()
        
    # remove the character on the cursor position
    def delete(self):
        front = self.cursorPosition + 1
        if front > len(self.equationString):
            front = len(self.equationString)
        self.equationString = self.equationString[:self.cursorPosition] + self.equationString[front:]
        self.writeEquation()

    # clear the equation
    def clearText(self):
        self.equationText.setText('_')
        self.equationString = ''
        self.cursorPosition = 0
        
    # computer the equation
    def compute(self):
        #TODO: call the interpreter to calculate the value
        answer = 123456.5
        self.history.addEquation(self.equationString, str(answer))
        self.clearText()
        self.addTextToEquation(str(answer))
        
def main(argv):

    app = QApplication(argv)
    app.setOrganizationName('comp354')
    app.setApplicationName('ETERNITY')

    # increase the foot size
    font = app.font()
    font.setPixelSize(22)
    app.setFont(font)
    
    # create the main window
    window = MainWindow(app)
    window.setWindowTitle('ETERNITY Calculator')
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main(sys.argv)