from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
import sys

# Sizes include 3/4, 2/3, 1/2
DEFAULT_HEIGHT = 540
DEFAULT_PEN_SIZE = 4
DEFAULT_ERASER_SIZE = 50


class Canvas(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()

        # Create canvas to paint on
        pixmap = QtGui.QPixmap(1920, 1080)
        pixmap.fill(Qt.transparent)
        self.setScaledContents(True)

        # Attach canvas to label and centralize it
        self.setPixmap(pixmap)
        self.last_pos = None
        self.pen_color = QtGui.QColor('#000000')
        self.drawing = True
        self.penSize = DEFAULT_PEN_SIZE
        self.eraserSize = DEFAULT_ERASER_SIZE
        self.displayRef = None
        self.prevState = pixmap

    def setPenSize(self, size):
        if size != "":
            self.penSize = int(size)

    def setEraserSize(self, size):
        self.eraserSize = int(size)

    def setDisplayRef(self, ref):
        self.displayRef = ref

    def setDrawing(self, isDrawing):
        self.drawing = isDrawing

    def setPenColor(self, c):
        self.pen_color = QtGui.QColor(c)

    def undoLast(self):
        self.setPixmap(self.prevState)
        if self.displayRef is not None:
            self.displayRef.updatePixmap(self.pixmap())

    def mousePressEvent(self, e):
        self.prevState = self.pixmap().copy()
        pm = QtGui.QPixmap(self.pixmap())

        painter = QtGui.QPainter(pm)

        if not self.drawing:
            painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)

        # Create and set pen for painting
        pen = painter.pen()
        if self.drawing:
            pen.setWidth(self.penSize)
        else:
            pen.setWidth(self.eraserSize)
        pen.setColor(self.pen_color)
        painter.setPen(pen)

        transform = QtGui.QTransform().scale(pm.width() / self.width(), pm.height() / self.height())
        painter.drawPoint(transform.map(e.pos()))
        painter.end()
        self.setPixmap(pm)
        if self.displayRef is not None:
            self.displayRef.updatePixmap(self.pixmap())

    def mouseMoveEvent(self, e):
        pm = QtGui.QPixmap(self.pixmap())
        if self.last_pos is None:
            self.last_pos = e.pos()
            return

        painter = QtGui.QPainter(pm)

        if not self.drawing:
            painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)

        # Create and set pen for painting
        pen = painter.pen()
        if self.drawing:
            pen.setWidth(self.penSize)
        else:
            pen.setWidth(self.eraserSize)
        pen.setColor(self.pen_color)
        painter.setPen(pen)
        transform = QtGui.QTransform().scale(pm.width() / self.width(), pm.height() / self.height())

        # Draw continuous line with pen
        painter.drawLine(transform.map(self.last_pos), transform.map(e.pos()))
        painter.end()
        self.setPixmap(pm)
        if self.displayRef is not None:
            self.displayRef.updatePixmap(self.pixmap())

        self.last_pos = e.pos()

    def mouseReleaseEvent(self, e):
        self.last_pos = None


COLORS = ['#000000', '#141923', '#414168', '#3a7fa7', '#35e3e3', '#8fd970', '#5ebb49',
          '#458352', '#dcd37b', '#fffee5', '#ffd035', '#cc9245', '#a15c3e', '#a42f3b',
          '#f45b7a', '#c24998', '#81588d', '#bcb0c2', '#ffffff']


class QPaletteButton(QtWidgets.QPushButton):

    def __init__(self, color):
        super().__init__()
        self.setFixedSize(QtCore.QSize(24, 24))
        self.color = color
        self.setStyleSheet("background-color: %s;" % color)


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

