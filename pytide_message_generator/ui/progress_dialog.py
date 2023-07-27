from PyQt6 import uic
from PyQt6.QtCore import QRunnable
from PyQt6.QtWidgets import QDialog, QProgressBar

class ProgressRunnable(QRunnable):

    def __init__(self):
        super(ProgressRunnable, self).__init__()
        self.dialog = ProgressDialog()

    def run(self):
        self.dialog.exec()

class ProgressDialog(QDialog):

    def __init__(self):
        super(ProgressDialog, self).__init__()

        self.generatorProgress: QProgressBar = None
        self.messageProgress: QProgressBar = None

        uic.loadUi('GUI/Windows/progress.ui', self)

    def setCounts(self, generatorCount: int, messageCount: int):
        self.generatorProgress.setMaximum(generatorCount)
        self.messageProgress.setMaximum(messageCount)

    def updateProgress(self, generator: int, generatorName: str):
        self.generatorProgress.setFormat("Generating {} (%v / %m)".format(generatorName))

        self.generatorProgress.setValue(generator)

    def updateMessageProgress(self, message: int):
        self.messageProgress.setValue(message)


    def runDialog(self):
        self.exec()
