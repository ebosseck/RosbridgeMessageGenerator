from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class ResizableStackWidget(QStackedWidget):

    stacksizechanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lastIDX = 0
        self.delta = 0
        self.currentChanged.connect(self.onCurrentChanged)

    def addWidget(self, w: QWidget) -> int:
        w.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        return super().addWidget(w)

    def onCurrentChanged(self):

        oldWidget = self.widget(self.lastIDX)
        oldWidget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        oldh = oldWidget.height()
        oldWidget.adjustSize()

        self.lastIDX = self.currentIndex()

        newWidget = self.widget(self.lastIDX)
        newWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        newWidget.adjustSize()
        self.delta = newWidget.height() - oldh
        self.adjustSize()
        self.stacksizechanged.emit()
