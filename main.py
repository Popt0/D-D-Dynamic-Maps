from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from canvas import *
from displayWindow import *

DEFAULT_MAT = 'Data/Mats/TreeStump.png'


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.canvas = Canvas()
        self.map = QtWidgets.QLabel()
        self.matFile = DEFAULT_MAT
        self.display = None

        # Create vertical box widget
        canvasWidget = QtWidgets.QWidget()
        canvasLayout = QtWidgets.QVBoxLayout()
        canvasWidget.setLayout(canvasLayout)

        # Add HBox containing window tools to VBox
        windowTools = QtWidgets.QHBoxLayout()
        self.addWindowTools(windowTools)
        canvasLayout.addLayout(windowTools)

        # Create grid for canvas/map
        # Scale image to viewport and overlay canvas, then add to VBox
        canvasGrid = QtWidgets.QGridLayout()
        policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Ignored)
        mapPixmap = QtGui.QPixmap(DEFAULT_MAT)
        self.map.setScaledContents(True)
        self.map.setPixmap(mapPixmap)
        self.map.setSizePolicy(policy)
        canvasGrid.addWidget(self.map, 0, 0)
        self.canvas.setSizePolicy(policy)
        canvasGrid.addWidget(self.canvas, 0, 0)
        canvasLayout.addLayout(canvasGrid)
        self.canvas.setMinimumSize(960, 540)
        self.canvas.setMaximumSize(int(1920 * .8), int(1080 * 0.8))

        # Add HBox containing palette buttons to VBox
        palette = QtWidgets.QHBoxLayout()
        self.addPaletteButtons(palette)
        canvasLayout.addLayout(palette)

        self.setCentralWidget(canvasWidget)


    # Initializes all the buttons used for drawing on the canvas. ie: colors and eraser
    def addPaletteButtons(self, layout):
        # Add undo button
        undo = QtWidgets.QPushButton()
        undo.setFixedSize(24, 24)
        undoPixmap = QtGui.QPixmap("Assets/undoIcon.png")
        undoIcon = QtGui.QIcon(undoPixmap)
        undo.setIcon(undoIcon)
        undo.setIconSize(QtCore.QSize(int(undo.width() / 1.2), int(undo.height() / 1.2)))
        undo.clicked.connect(lambda: self.canvas.undoLast())
        layout.addWidget(undo)

        # Add pen size option
        penSizeBox = QSizeInput("Pen:", 2)
        penSizeBox.input.setText(str(DEFAULT_PEN_SIZE))
        penSizeBox.input.textChanged.connect(lambda: self.canvas.setPenSize(penSizeBox.getText()))
        layout.addLayout(penSizeBox)

        # Add buttons for color choices
        for color in COLORS:
            button = QPaletteButton(color)
            button.pressed.connect(lambda c=color: self.canvas.setPenColor(c))
            button.pressed.connect(lambda: self.canvas.setDrawing(True))
            layout.addWidget(button)

        # Add eraser size option
        eraserSizeBox = QSizeInput("Eraser:", 2)
        eraserSizeBox.input.setText(str(DEFAULT_ERASER_SIZE))
        eraserSizeBox.input.textChanged.connect(lambda: self.canvas.setEraserSize(eraserSizeBox.getText()))
        layout.addLayout(eraserSizeBox)

        # Add eraser button
        button = QPaletteButton(Qt.transparent)
        button.pressed.connect(lambda: self.canvas.setDrawing(False))
        buttonPixmap = QtGui.QPixmap("Assets/eraserIcon.png")
        buttonIcon = QtGui.QIcon(buttonPixmap)
        button.setIcon(buttonIcon)
        button.setIconSize(QtCore.QSize(int(button.width()/1.2), int(button.height()/1.2)))
        layout.addWidget(button)

    def addWindowTools(self, layout):
        # Add the open map from file icon
        fileSelect = QtWidgets.QPushButton()
        fileSelect.setFixedSize(24, 24)
        fileSelectPixmap = QtGui.QPixmap("Assets/openFileIcon.png")
        fileSelectIcon = QtGui.QIcon(fileSelectPixmap)
        fileSelect.setIcon(fileSelectIcon)
        fileSelect.setIconSize(QtCore.QSize(int(fileSelect.width()/1.2), int(fileSelect.height()/1.2)))
        fileSelect.clicked.connect(self.promptMapFile)
        layout.addWidget(fileSelect)

        # Add the window pop out button
        popOut = QtWidgets.QPushButton()
        popOut.setFixedSize(24, 24)
        popOutPixmap = QtGui.QPixmap("Assets/popOutIcon.png")
        popOutIcon = QtGui.QIcon(popOutPixmap)
        popOut.setIcon(popOutIcon)
        popOut.setIconSize(QtCore.QSize(int(popOut.width()/1.2), int(popOut.height()/1.2)))
        popOut.clicked.connect(self.popOutWindow)
        layout.addWidget(popOut)

        # Add full screen toggle button
        fullScreen = QtWidgets.QPushButton()
        fullScreen.setFixedSize(24, 24)
        fullScreenPixmap = QtGui.QPixmap("Assets/fullScreenIcon.png")
        fullScreenIcon = QtGui.QIcon(fullScreenPixmap)
        fullScreen.setIcon(fullScreenIcon)
        fullScreen.setIconSize(QtCore.QSize(int(fullScreen.width() / 1.2), int(fullScreen.height() / 1.2)))
        fullScreen.clicked.connect(self.toggleFullScreen)
        layout.addWidget(fullScreen)

    def promptMapFile(self):
        fileDialog = QtWidgets.QFileDialog()
        fileDialog.setNameFilter("Images (*.png *.jpg)")

        if fileDialog.exec():
            files = fileDialog.selectedFiles()
            print(files[0])
            self.matFile = files[0]
            self.updateMat()


    # Creates Display Window if none are currently active
    def popOutWindow(self):
        if self.display is None:
            self.display = DisplayWindow(self.matFile, self.canvas.pixmap())
            self.canvas.setDisplayRef(self.display)
        self.display.show()

    # Toggles whether display window is in full screen mode
    def toggleFullScreen(self):
        if self.display is not None:
            if self.display.isFullScreen():
                self.display.showNormal()
            else:
                self.display.showFullScreen()

    def updateMat(self):
        newPixmap = QtGui.QPixmap(self.matFile)
        self.map.setPixmap(newPixmap)

        if self.display is not None:
            self.display.map.setPixmap(newPixmap)


app = QtWidgets.QApplication(sys.argv)

# Create and open main window of the application
window = MainWindow()
window.show()

app.exec_()


