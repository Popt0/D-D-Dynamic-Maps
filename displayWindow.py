from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt


class DisplayWindow(QtWidgets.QMainWindow):
    def __init__(self, mat, canvasPixmap):
        super().__init__()

        self.map = QtWidgets.QLabel()
        self.canvas = QtWidgets.QLabel()

        mapWidget = QtWidgets.QWidget()
        mapGrid = QtWidgets.QGridLayout()
        mapGrid.setContentsMargins(0, 0, 0, 0)
        mapWidget.setLayout(mapGrid)
        self.setCentralWidget(mapWidget)

        mapPixmap = QtGui.QPixmap(mat)
        self.map.setScaledContents(True)
        self.map.setPixmap(mapPixmap)
        self.map.setFixedSize(1920, 1080)

        self.canvas.setScaledContents(True)
        self.canvas.setPixmap(canvasPixmap)
        self.canvas.setFixedSize(1920, 1080)

        mapGrid.addWidget(self.map, 0, 0)
        mapGrid.addWidget(self.canvas, 0, 0)

    def updatePixmap(self, newMap):
        self.canvas.setPixmap(newMap)

    def toggleFullScreen(self):
        if self.isFullscreen():
            self.showNormal()
        else:
            self.showFullscreen()

