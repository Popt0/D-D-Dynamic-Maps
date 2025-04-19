from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

from enum import Enum

DEFAULT_PEN_SIZE = 4
DEFAULT_ERASER_SIZE = 50


# Different modes the mouse can be in
class MouseMode(Enum):
    Drawing = 0
    Erasing = 1
    Panning = 2


# Scene that contains all active 2D objects
class QMapScene(QtWidgets.QGraphicsScene):
    def __init__(self, mapFile):
        super().__init__()

        self.mapItem = QCanvasItem(QtGui.QPixmap(mapFile))
        self.mapItem.setTransformationMode(Qt.SmoothTransformation)
        self.addItem(self.mapItem)


# Viewport for displaying the scene to the editor
class QScalingView(QtWidgets.QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.mapItem = scene.mapItem

        self.mouseMode = MouseMode.Drawing
        self.lastPos = None

        self.zoomFactor = 1.0

    #Handles mouse presses to begin panning
    def mousePressEvent(self, event):
        if self.mouseMode == MouseMode.Panning:
            self.lastPos = event.pos()
        else:
            super().mousePressEvent(event)

    # Handles mouse moving to pan viewport
    def mouseMoveEvent(self, event):
        if self.mouseMode == MouseMode.Panning:
            pan = self.lastPos - event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + pan.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + pan.y())
            self.lastPos = event.pos()
        else:
            super().mouseMoveEvent(event)

    # Handles scrolling to zoom the viewport
    def wheelEvent(self, event):
        zoomStep = 0.05

        if event.angleDelta().y() > 0:
            self.zoomFactor += zoomStep
        else:
            self.zoomFactor -= zoomStep
            if self.zoomFactor < 0.1:
                self.zoomFactor = 0.1

        transform = QtGui.QTransform()
        transform.scale(self.zoomFactor, self.zoomFactor)
        self.setTransform(transform)

    #sets a new value for the mouse input mode
    def setMouseMode(self, mode):
        self.mouseMode = mode
        self.mapItem.setMouseMode(mode)

        if mode == MouseMode.Drawing:
            cursorPixmap = QtGui.QPixmap("Assets/penCursor.png")
            cursorPixmap = cursorPixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setCursor(QtGui.QCursor(cursorPixmap, hotX=6, hotY=26))
        elif mode == MouseMode.Erasing:
            cursorPixmap = QtGui.QPixmap("Assets/eraserCursor.png")
            cursorPixmap = cursorPixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setCursor(QtGui.QCursor(cursorPixmap, hotX=4, hotY=20))
        elif mode == MouseMode.Panning:
            self.setCursor(QtGui.QCursor(Qt.OpenHandCursor))


class QCanvasItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        scaledMap = self.pixmap().scaled(1920, 1080, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(scaledMap)
        self.mapPixmap = self.pixmap().copy()
        self.canvasPixmap = QtGui.QPixmap(1920, 1080)
        self.canvasPixmap.fill(Qt.transparent)

        self.prevState = self.canvasPixmap.copy()
        self.penSize = DEFAULT_PEN_SIZE
        self.eraserSize = DEFAULT_ERASER_SIZE
        self.isDrawing = True
        self.penColor = QtGui.QColor('#000000')
        self.lastPos = None

        self.displayRef = None
        self.mouseMode = MouseMode.Drawing

    #Updates the map in viewport and display by drawing edited maps over the main mat
    def updateMap(self):
        newPixmap = self.mapPixmap.copy()
        painter = QtGui.QPainter(newPixmap)
        painter.drawPixmap(0, 0, 1920, 1080, self.canvasPixmap)
        painter.end()
        self.setPixmap(newPixmap)

        if self.displayRef is not None:
            self.displayRef.updatePixmap(newPixmap)

    # Resets canvas with new map scaled to fit 1920x1080 display
    def setNewMap(self, mapFile):
        self.mapPixmap = QtGui.QPixmap(mapFile)
        self.mapPixmap = self.mapPixmap.scaled(1920, 1080, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.canvasPixmap = QtGui.QPixmap(1920, 1080)
        self.canvasPixmap.fill(Qt.transparent)
        self.updateMap()

    # Handles mouse presses to begin drawing/erasing
    def mousePressEvent(self, event):
        if self.mouseMode == MouseMode.Drawing or self.mouseMode == MouseMode.Erasing:
            self.lastPos = event.pos()
            self.prevState = self.canvasPixmap.copy()
            painter = QtGui.QPainter(self.canvasPixmap)

            pen = painter.pen()
            if self.mouseMode == MouseMode.Erasing:
                painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)
                pen.setWidth(self.eraserSize)
            else:
                pen.setWidth(self.penSize)

            pen.setColor(self.penColor)
            painter.setPen(pen)
            painter.drawPoint(event.pos())
            painter.end()
            self.updateMap()

    # Handles mouse movement to draw/erase in a continuous line
    def mouseMoveEvent(self, event):
        if self.mouseMode == MouseMode.Drawing or self.mouseMode == MouseMode.Erasing:
            painter = QtGui.QPainter(self.canvasPixmap)
            if self.lastPos is None:
                self.lastPos = event.pos()
                return

            pen = painter.pen()
            if self.mouseMode == MouseMode.Erasing:
                painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)
                pen.setWidth(self.eraserSize)
            else:
                pen.setWidth(self.penSize)
            pen.setColor(self.penColor)
            painter.setPen(pen)

            painter.drawLine(self.lastPos, event.pos())
            painter.end()
            self.updateMap()
            self.lastPos = event.pos()

    # Handles mouse release to record last mouse position
    def mouseReleaseEvent(self, event):
        self.lastPos = None

    # Connects canvas to the display window
    def setDisplayRef(self, ref):
        self.displayRef = ref

    # Returns the canvas to it's previous state
    def undoLast(self):
        self.canvasPixmap = self.prevState
        self.updateMap()
        if self.displayRef is not None:
            self.displayRef.updatePixmap(self.pixmap())

    # Sets a new size for the draw tool
    def setPenSize(self, size):
        if size != "":
            self.penSize = int(size)

    # Sets a new size for the erase tool
    def setEraserSize(self, size):
        if size != "":
            self.eraserSize = int(size)

    # delete soon
    def setDrawing(self, drawing):
        self.isDrawing = drawing

    # Sets a color for the draw tool
    def setPenColor(self, color):
        self.penColor = QtGui.QColor(color)

    # sets mouse input mode for canvas
    def setMouseMode(self, mode):
        self.mouseMode = mode


class QDisplayWindow(QtWidgets.QMainWindow):
    def __init__(self, pixmap):
        super().__init__()

        self.map = QtWidgets.QLabel()

        self.setCentralWidget(self.map)
        self.map.setScaledContents(True)
        self.map.setPixmap(pixmap)

    def updatePixmap(self, newMap):
        self.map.setPixmap(newMap)

    def toggleFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullscreen()
