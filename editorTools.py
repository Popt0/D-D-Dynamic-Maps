from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

COLORS = ['#000000', '#141923', '#414168', '#3a7fa7', '#35e3e3', '#8fd970', '#5ebb49',
          '#458352', '#dcd37b', '#fffee5', '#ffd035', '#cc9245', '#a15c3e', '#a42f3b',
          '#f45b7a', '#c24998', '#81588d', '#bcb0c2', '#ffffff']


class QPaletteButton(QtWidgets.QPushButton):
    def __init__(self, color):
        super().__init__()
        self.setFixedSize(QtCore.QSize(24, 24))
        self.color = color
        self.setStyleSheet("background-color: %s;" % color)


class QIconButton(QtWidgets.QPushButton):
    def __init__(self, iconPath):
        super().__init__()
        self.setFixedSize(QtCore.QSize(24, 24))
        pm = QtGui.QPixmap(iconPath)
        icon = QtGui.QIcon(pm)
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(int(self.width()/1.2), int(self.height()/1.2)))



class QSizeInput(QtWidgets.QHBoxLayout):
    def __init__(self, text, charLimit):
        super().__init__()

        self.setContentsMargins(0, 0, 0, 0)
        self.maxChars = charLimit

        self.text = QtWidgets.QLabel()
        self.text.setText(text)
        self.text.setFixedSize(len(text) * 5, 24)
        self.addWidget(self.text)

        self.input = QtWidgets.QTextEdit()
        self.input.setFixedSize(charLimit * 14, 24)
        self.input.textChanged.connect(self.checkText)
        self.addWidget(self.input)

    def checkText(self):
        newString = ""
        change = False

        for char in self.input.toPlainText():
            if char.isdigit():
                newString = newString + char
            else:
                change = True

        if change:
            self.input.setText(newString)

        if len(newString) > self.maxChars:
            self.input.setText(self.input.toPlainText()[:self.maxChars])
            print(self.input.toPlainText())

    def getText(self):
        return self.input.toPlainText()