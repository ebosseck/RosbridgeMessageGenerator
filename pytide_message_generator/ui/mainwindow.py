from PyQt6.QtCore import *
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        uic.loadUi('GUI/Windows/mainwindow.ui', self)
        self.loadPlugins()

    def loadPlugins(self):
        pass