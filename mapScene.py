from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

from enum import Enum
import math

DEFAULT_PEN_SIZE = 4
DEFAULT_ERASER_SIZE = 50
DEFAULT_FIVE_FOOT_SIZE = 50
DEFAULT_SPELL_SIZE_FT = 10

MEASURE_SQUARE_COLOR = QtGui.QColor("#FF0000")
MEASURE_SQUARE_OPACITY = 0.2
MEASURE_SQUARE_WIDTH = 2
SPELL_WIDTH = 4
SPELL_OPACITY = 0.3


# Different modes the mouse can be in
class MouseMode(Enum):
    Drawing = 0
    Erasing = 1
    Panning = 2
    Measuring = 3
    Casting = 4

class SpellType(Enum):
    Square = 0
    Circle = 1
    Cone = 2


# Scene that contains all active 2D objects
class QMapScene(QtWidgets.QGraphicsScene):
    def __init__(self, mapFile):
        super().__init__()

        self.mapItem = QCanvasItem(QtGui.QPixmap(mapFile))
        self.mapItem.setTransformationMode(Qt.SmoothTransformation)
        self.addItem(self.mapItem)


# Viewport for displaying the scene to the primary user
class QScalingView(QtWidgets.QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.mapItem = scene.mapItem
        self.mouseMode = MouseMode.Drawing
        self.lastPos = None

        self.zoomFactor = 1.0

        self.setMouseMode(MouseMode.Drawing)

    # Handles mouse presses to begin panning
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

    # Sets a new value for the mouse input mode
    def setMouseMode(self, mode):
        self.mouseMode = mode
        self.mapItem.setMouseMode(mode)
        self.mapItem.setAcceptHoverEvents(False)

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
        elif mode == MouseMode.Measuring:
            self.setCursor(QtGui.QCursor(Qt.CrossCursor))
        elif mode == MouseMode.Casting:
            self.mapItem.setAcceptHoverEvents(True)
            self.setCursor(QtGui.QCursor(Qt.PointingHandCursor))


# Primary viewport for map that can be edited allowing for markings or effects on the map to appear to players
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
        self.penColor = QtGui.QColor('#000000')
        self.lastPos = QtCore.QPoint()

        self.fiveFootSize = DEFAULT_FIVE_FOOT_SIZE
        self.measureStart = QtCore.QPoint()
        self.measureEnd = QtCore.QPoint()
        self.measureLabelRef = QtWidgets.QLabel()
        self.preservedState = self.canvasPixmap.copy()

        self.spellSizeFt = DEFAULT_SPELL_SIZE_FT
        self.spellSize = int((DEFAULT_SPELL_SIZE_FT / 5) * DEFAULT_FIVE_FOOT_SIZE)
        self.spellType = SpellType.Square
        self.coneOrigin = None
        self.showPlayers = True

        self.displayRef = None
        self.mouseMode = MouseMode.Drawing

    # Updates the map in viewport and display by drawing edited maps over the main mat
    def updateMap(self, updateDisplay=True):
        newPixmap = self.mapPixmap.copy()
        painter = QtGui.QPainter(newPixmap)
        painter.drawPixmap(0, 0, 1920, 1080, self.canvasPixmap)
        painter.end()
        self.setPixmap(newPixmap)

        if self.displayRef is not None and updateDisplay:
            self.displayRef.updatePixmap(newPixmap)

    # Resets canvas with new map scaled to fit 1920x1080 display
    def setNewMap(self, mapFile):
        self.mapPixmap = QtGui.QPixmap(mapFile)
        self.mapPixmap = self.mapPixmap.scaled(1920, 1080, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.canvasPixmap = QtGui.QPixmap(1920, 1080)
        self.canvasPixmap.fill(Qt.transparent)
        self.prevState = self.canvasPixmap.copy()
        self.preservedState = self.canvasPixmap.copy()
        self.updateMap()

    # Handles mouse presses depending on current mouse mode
    def mousePressEvent(self, event):
        # Drawing and erasing mouse press event handler
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
            self.preservedState = self.canvasPixmap.copy()
        # Casting mouse press event handler
        elif self.mouseMode == MouseMode.Casting:
            if self.spellType == SpellType.Cone:
                if self.coneOrigin is None:
                    self.coneOrigin = event.pos().toPoint()
                    return

            self.prevState = self.preservedState.copy()
            self.updateMap()
            self.preservedState = self.canvasPixmap.copy()
            self.coneOrigin = None
        # Measuring mouse press event handler
        elif self.mouseMode == MouseMode.Measuring:
            self.measureStart = event.pos().toPoint()
            self.measureEnd = event.pos().toPoint()

    # Handles mouse movement depending on current mouse mode
    def mouseMoveEvent(self, event):
        # Drawing and erasing mouse move event handler
        if self.mouseMode == MouseMode.Drawing or self.mouseMode == MouseMode.Erasing:
            painter = QtGui.QPainter(self.canvasPixmap)

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
            self.preservedState = self.canvasPixmap.copy()
        # Measuring mouse move event handler
        elif self.mouseMode == MouseMode.Measuring:
            mouseEnd = event.pos().toPoint()
            xDiff = self.measureStart.x() - mouseEnd.x()
            yDiff = self.measureStart.y() - mouseEnd.y()

            # Makes Y distance the same as X distance if X distance is wider
            if abs(xDiff) > abs(yDiff):
                # Makes the square go upwards if mouse is higher than where it started
                if yDiff > 0:
                    yAdjusted = self.measureStart.y() - abs(xDiff)
                    self.measureEnd = QtCore.QPoint(mouseEnd.x(), yAdjusted)
                # Makes the square go downwards if mouse is lower than or the same as where it started
                else:
                    yAdjusted = self.measureStart.y() + abs(xDiff)
                    self.measureEnd = QtCore.QPoint(mouseEnd.x(), yAdjusted)
            # Makes X distance the same as Y distance if Y distance is wider
            else:
                # Makes the square go left if mouse is left of where it started
                if xDiff > 0:
                    xAdjusted = self.measureStart.x() - abs(yDiff)
                    self.measureEnd = QtCore.QPoint(xAdjusted, mouseEnd.y())
                # Makes the square go right if the mouse is right of or the same as where it started
                else:
                    xAdjusted = self.measureStart.x() + abs(yDiff)
                    self.measureEnd = QtCore.QPoint(xAdjusted, mouseEnd.y())

            newCanvasPixmap = self.preservedState.copy()
            painter = QtGui.QPainter(newCanvasPixmap)

            pen = QtGui.QPen()
            pen.setColor(MEASURE_SQUARE_COLOR)
            pen.setWidth(MEASURE_SQUARE_WIDTH)
            painter.setPen(pen)

            brushColor = QtGui.QColor(MEASURE_SQUARE_COLOR)
            brushColor.setAlphaF(MEASURE_SQUARE_OPACITY)
            brush = QtGui.QBrush(brushColor, Qt.SolidPattern)

            measureRect = QtCore.QRect(self.measureStart, self.measureEnd)
            painter.drawRect(measureRect.normalized())
            painter.fillRect(measureRect, brush)

            painter.end()

            self.canvasPixmap = newCanvasPixmap
            self.updateMap(updateDisplay=False)

    # Handles mouse hover events depending on current mouse mode
    def hoverMoveEvent(self, event):
        # Handles casting mouse hover events
        if self.mouseMode == MouseMode.Casting:
            if self.spellType != SpellType.Cone or self.coneOrigin is not None:
                newCanvasPixmap = self.preservedState.copy()
                painter = QtGui.QPainter(newCanvasPixmap)

                pen = QtGui.QPen()
                pen.setColor(self.penColor)
                pen.setWidth(SPELL_WIDTH)
                painter.setPen(pen)

                brushColor = QtGui.QColor(self.penColor)
                brushColor.setAlphaF(SPELL_OPACITY)
                brush = QtGui.QBrush(brushColor, Qt.SolidPattern)
                painter.setBrush(brush)

                if self.spellType == SpellType.Square:
                    rectX = int(event.pos().x() - (self.spellSize / 2))
                    rectY = int(event.pos().y() - (self.spellSize / 2))
                    rectTopLeft = QtCore.QPoint(rectX, rectY)
                    spellRect = QtCore.QRect(rectTopLeft, QtCore.QSize(self.spellSize, self.spellSize))
                    painter.drawRect(spellRect)
                elif self.spellType == SpellType.Circle:
                    painter.drawEllipse(event.pos().toPoint(), self.spellSize, self.spellSize)
                else:
                    xDiff = event.pos().toPoint().x() - self.coneOrigin.x()
                    yDiff = event.pos().toPoint().y() - self.coneOrigin.y()
                    dist = math.sqrt(pow(abs(xDiff), 2) + pow(abs(yDiff), 2))

                    if dist != 0:
                        # Get ratio of spellSizes to distance of mouse from origin then calc cone end point
                        ratio = self.spellSize / dist
                        xMid = (xDiff * ratio) + self.coneOrigin.x()
                        yMid = (yDiff * ratio) + self.coneOrigin.y()

                        # Make corners by going out in both directions half of spellSize(diff * ratio)
                        # using an opposite slope
                        corner1 = QtCore.QPoint(int(xMid - ((yDiff * ratio)/2)),
                                                int(yMid + ((xDiff * ratio)/2)))
                        corner2 = QtCore.QPoint(int(xMid + ((yDiff * ratio)/2)),
                                                int(yMid - ((xDiff * ratio)/2)))
                    else:
                        # Set default corners for when mouse has not moved
                        corner1 = QtCore.QPoint(int(self.coneOrigin.x() - (self.spellSize / 2)),
                                                self.coneOrigin.y() + self.spellSize)
                        corner2 = QtCore.QPoint(int(self.coneOrigin.x() + (self.spellSize / 2)),
                                                self.coneOrigin.y() + self.spellSize)

                    conePolygon = QtGui.QPolygon()
                    conePolygon << self.coneOrigin << corner1 << corner2
                    painter.drawPolygon(conePolygon)

                painter.end()

                self.canvasPixmap = newCanvasPixmap
                self.updateMap(updateDisplay=self.showPlayers)

    # Handles mouse leaving hover range depending on mouse mode
    def hoverLeaveEvent(self, event):
        if self.mouseMode == MouseMode.Casting:
            self.canvasPixmap = self.preservedState
            self.updateMap()

    # Handles mouse release events depending on current mouse mode
    def mouseReleaseEvent(self, event):
        # Drawing and erasing mouse release event handler
        if self.mouseMode == MouseMode.Drawing or self.mouseMode == MouseMode.Erasing:
            self.lastPos = QtCore.QPoint()
        # Measuring mouse release event handler
        elif self.mouseMode == MouseMode.Measuring:
            if self.measureEnd == self.measureStart:
                return
            self.canvasPixmap = self.preservedState
            self.fiveFootSize = abs(self.measureStart.x() - self.measureEnd.x())
            self.setSpellSize(self.spellSizeFt)
            self.measureLabelRef.setText("5 ft: %s px" % self.fiveFootSize)
            self.updateMap()

    # Connects canvas to the display window
    def setDisplayRef(self, ref):
        self.displayRef = ref

    # Returns the canvas to its previous state
    def undoLast(self):
        self.canvasPixmap = self.prevState
        self.updateMap()
        if self.displayRef is not None:
            self.displayRef.updatePixmap(self.pixmap())
        self.preservedState = self.canvasPixmap.copy()

    # Sets a new size for the draw tool
    def setPenSize(self, size):
        if size != "":
            self.penSize = int(size)

    # Sets a new size for the erase tool
    def setEraserSize(self, size):
        if size != "":
            self.eraserSize = int(size)

    # Sets a color for the draw tool
    def setPenColor(self, color):
        self.penColor = QtGui.QColor(color)

    # sets mouse input mode for canvas
    def setMouseMode(self, mode):
        self.mouseMode = mode

    # Sets the text for the label displaying pixel value of a 5 ft distance
    def setMeasureLabel(self, label):
        self.measureLabelRef = label

    # Sets the spell size for both ft and px
    def setSpellSize(self, size):
        if size != "":
            size = int(size)
            self.spellSizeFt = size
            self.spellSize = ((self.fiveFootSize * int(size / 5)) +
                              ((size % 5) * int(self.fiveFootSize / 5)))

    # Sets the spell type to the spell currently being cast
    def setSpellType(self, spellType):
        self.spellType = spellType

    # Sets whether players can see spell rulers before cast
    def setShowPlayers(self, show):
        self.showPlayers = show


# Window that displays the edited map to the players
class QDisplayWindow(QtWidgets.QMainWindow):
    def __init__(self, pixmap):
        super().__init__()

        self.map = QtWidgets.QLabel()

        self.setCentralWidget(self.map)
        self.map.setScaledContents(True)
        self.map.setPixmap(pixmap)

    # sets the battle mat to a different one
    def updatePixmap(self, newMap):
        self.map.setPixmap(newMap)
