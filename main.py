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

        spellLayout = QtWidgets.QHBoxLayout()
        self.addSpellTools(spellLayout)
        mainLayout.addLayout(spellLayout)

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

    # Initializes tools for editing and navigating the map viewport
    def addEditorTools(self, layout):
        # Add file select button
        fileSelect = QIconButton("Assets/openFileIcon.png")
        fileSelect.clicked.connect(lambda: self.promptMapFile())
        layout.addWidget(fileSelect)

        # Add pop out display button
        popOut = QIconButton("Assets/popOutIcon.png")
        popOut.clicked.connect(lambda: self.openDisplay())
        layout.addWidget(popOut)

        # Add toggle display full screen button
        fullScreen = QIconButton("Assets/fullScreenIcon.png")
        fullScreen.clicked.connect(lambda: self.toggleDisplayFullScreen())
        layout.addWidget(fullScreen)

        # Add panning button
        pan = QIconButton("Assets/panningIcon.png")
        pan.clicked.connect(lambda: self.mapView.setMouseMode(MouseMode.Panning))
        layout.addWidget(pan)

    # Initializes tools for declaring tile size and spell rulers
    def addSpellTools(self, layout):
        layout.addStretch()

        # Add measuring button for spell rulers
        measureBox = QtWidgets.QHBoxLayout()
        measureBox.setContentsMargins(0, 0, 0, 0)
        measure = QIconButton("Assets/rulerIcon.png")
        measure.clicked.connect(lambda: self.mapView.setMouseMode(MouseMode.Measuring))
        measureBox.addWidget(measure)
        measureLabel = QtWidgets.QLabel()
        measureLabel.setText("5 ft: %s px" % self.mapScene.mapItem.fiveFootSize)
        measureBox.addWidget(measureLabel)
        self.mapScene.mapItem.setMeasureLabel(measureLabel)
        layout.addLayout(measureBox)

        layout.addStretch()

        # Add check box to allow players to see spells before they are cast
        showPlayerBox = QtWidgets.QCheckBox()
        showPlayerBox.setChecked(True)
        showPlayerBox.setText("Show to Players")
        showPlayerBox.clicked.connect(lambda: self.mapScene.mapItem.setShowPlayers(showPlayerBox.checkState()))
        layout.addWidget(showPlayerBox)

        layout.addStretch()

        # Add size input for spell casting
        spellSize = QSizeInput("Spell Size:", 3)
        spellSize.input.setText(str(DEFAULT_SPELL_SIZE_FT))
        spellSize.input.textChanged.connect(lambda: self.mapScene.mapItem.setSpellSize(spellSize.getText()))
        ftLabel = QtWidgets.QLabel()
        ftLabel.setText("ft")
        spellSize.addWidget(ftLabel)
        layout.addLayout(spellSize)

        layout.addStretch()

        # Add button for square spells
        squareButton = QIconButton("Assets/squareIcon.png")
        squareButton.clicked.connect(lambda: self.mapView.setMouseMode(MouseMode.Casting))
        squareButton.clicked.connect(lambda: self.mapView.mapItem.setSpellType(SpellType.Square))
        layout.addWidget(squareButton)

        # Add button for circular spells
        circleButton = QIconButton("Assets/circleIcon.png")
        circleButton.clicked.connect(lambda: self.mapView.setMouseMode(MouseMode.Casting))
        circleButton.clicked.connect(lambda: self.mapView.mapItem.setSpellType(SpellType.Circle))
        layout.addWidget(circleButton)

        # Add button for conic spells
        coneButton = QIconButton("Assets/coneIcon.png")
        coneButton.clicked.connect(lambda: self.mapView.setMouseMode(MouseMode.Casting))
        coneButton.clicked.connect(lambda: self.mapView.mapItem.setSpellType(SpellType.Cone))
        layout.addWidget(coneButton)

        layout.addStretch()

    # Opens the display window for the player monitor
    def openDisplay(self):
        self.displayMap = QDisplayWindow(self.mapScene.mapItem.pixmap())
        self.displayMap.show()
        self.mapScene.mapItem.setDisplayRef(self.displayMap)

    # Toggles full screen on the display window
    def toggleDisplayFullScreen(self):
        if self.displayMap.isVisible:
            if self.displayMap.isFullScreen():
                self.displayMap.showNormal()
            else:
                self.displayMap.showFullScreen()

    # Opens a file explorer to select the battle mat file
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