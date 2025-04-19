from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
import sys

from mapScene import *
from editorTools import *

DEFAULT_MAT = 'Data/Mats/Test.png'


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        mainWidget = QtWidgets.QWidget()
        mainLayout = QtWidgets.QVBoxLayout()
        mainWidget.setLayout(mainLayout)

        displayLayout = QtWidgets.QHBoxLayout()
        self.addEditorTools(displayLayout)
        mainLayout.addLayout(displayLayout)

        self.mapScene = QMapScene(DEFAULT_MAT)
        self.mapView = QScalingView(self.mapScene)
        mainLayout.addWidget(self.mapView)

        paintLayout = QtWidgets.QHBoxLayout()
        self.addPaletteTools(paintLayout)
        mainLayout.addLayout(paintLayout)

        self.setCentralWidget(mainWidget)
        self.mapView.show()

        self.displayMap = QDisplayWindow(QtGui.QPixmap())

    # Initializes all the buttons used for drawing on the canvas. ie: colors and eraser
    def addPaletteTools(self, layout):
        # Add undo button
        undo = QtWidgets.QPushButton()
        undo.setFixedSize(24, 24)
        undoPixmap = QtGui.QPixmap("Assets/undoIcon.png")
        undoIcon = QtGui.QIcon(undoPixmap)
        undo.setIcon(undoIcon)
        undo.setIconSize(QtCore.QSize(int(undo.width() / 1.2), int(undo.height() / 1.2)))
        undo.clicked.connect(lambda: self.mapScene.mapItem.undoLast())
        layout.addWidget(undo)

        # Add pen size option
        penSizeBox = QSizeInput("Pen:", 2)
        penSizeBox.input.setText(str(DEFAULT_PEN_SIZE))
        penSizeBox.input.textChanged.connect(lambda: self.mapScene.mapItem.setPenSize(penSizeBox.getText()))
        layout.addLayout(penSizeBox)

        # Add buttons for color choices
        for color in COLORS:
            button = QPaletteButton(color)
            button.pressed.connect(lambda c=color: self.mapScene.mapItem.setPenColor(c))
            button.pressed.connect(lambda: self.mapView.setMouseMode(MouseMode.Drawing))
            layout.addWidget(button)

        # Add eraser size option
        eraserSizeBox = QSizeInput("Eraser:", 2)
        eraserSizeBox.input.setText(str(DEFAULT_ERASER_SIZE))
        eraserSizeBox.input.textChanged.connect(lambda: self.mapScene.mapItem.setEraserSize(eraserSizeBox.getText()))
        layout.addLayout(eraserSizeBox)

        # Add eraser button
        erase = QPaletteButton(Qt.transparent)
        erase.pressed.connect(lambda: self.mapView.setMouseMode(MouseMode.Erasing))
        erasePixmap = QtGui.QPixmap("Assets/eraserIcon.png")
        eraseIcon = QtGui.QIcon(erasePixmap)
        erase.setIcon(eraseIcon)
        erase.setIconSize(QtCore.QSize(int(erase.width()/1.2), int(erase.height()/1.2)))
        layout.addWidget(erase)

    def addEditorTools(self, layout):
        fileSelect = QIconButton("Assets/openFileIcon.png")
        fileSelect.clicked.connect(lambda: self.promptMapFile())
        layout.addWidget(fileSelect)

        popOut = QIconButton("Assets/popOutIcon.png")
        popOut.clicked.connect(lambda: self.openDisplay())
        layout.addWidget(popOut)

        fullScreen = QIconButton("Assets/fullScreenIcon.png")
        fullScreen.clicked.connect(lambda: self.toggleDisplayFullScreen())
        layout.addWidget(fullScreen)

        pan = QIconButton("Assets./panningIcon.png")
        pan.clicked.connect(lambda: self.mapView.setMouseMode(MouseMode.Panning))
        layout.addWidget(pan)

    def openDisplay(self):
        self.displayMap = QDisplayWindow(self.mapScene.mapItem.pixmap())
        self.displayMap.show()
        self.mapScene.mapItem.setDisplayRef(self.displayMap)

    def toggleDisplayFullScreen(self):
        if self.displayMap.isVisible:
            if self.displayMap.isFullScreen():
                self.displayMap.showNormal()
            #self.displayMap.showFullScreen()
            else:
                self.displayMap.showFullScreen()

    def promptMapFile(self):
        fileDialog = QtWidgets.QFileDialog()
        fileDialog.setNameFilter("Images (*.png *.jpg *.jpeg)")

        if fileDialog.exec():
            files = fileDialog.selectedFiles()
            self.mapScene.mapItem.setNewMap(files[0])


app = QtWidgets.QApplication(sys.argv)

# Create and open main window of the application
window = MainWindow()
window.show()

app.exec_()