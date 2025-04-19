from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt


class QDisplayWindow(QtWidgets.QMainWindow):
    def __init__(self, pixmap):
        super().__init__()

        self.map = QtWidgets.QLabel()

        self.setCentralWidget(self.map)
        self.map.setScaledContents(True)
        self.map.setPixmap(pixmap)

    def updatePixmap(self, newMap):
        self.map.setPixmap(newMap)