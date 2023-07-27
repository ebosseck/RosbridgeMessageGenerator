import sys
from time import sleep
from typing import Dict, List

from PyQt6 import uic
from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, QThread, QThreadPool
from PyQt6.QtWidgets import QMainWindow, QComboBox, QGroupBox, QAbstractButton, QToolButton, QCheckBox, QTabWidget, \
    QLineEdit, QPushButton, QTreeView, QAbstractItemView, QProgressDialog

from pytide_message_generator.dataprovider.idataprovider import IDataProvider
from pytide_message_generator.dataprovider.message_data import MessageData
from pytide_message_generator.generator.igenerator import IGenerator
from pytide_message_generator.plugin import moduleloader
from pytide_message_generator.settings.settings import COLUMNS_LANGUAGE_LAYOUT
from pytide_message_generator.tools.ui_interaction_tools import setup_folder_select
from pytide_message_generator.ui.progress_dialog import ProgressDialog, ProgressRunnable
from pytide_message_generator.widgets.messageView.messagedatarole import DATA_ROLE_MESSAGE_DATA
from pytide_message_generator.widgets.messageView.messagemodel import MessageModel
from pytide_message_generator.widgets.messageView.messageview import MessageView
from pytide_message_generator.widgets.messageView.messagewidget import MessageWidget
from pytide_message_generator.widgets.resizeablestackwidget import ResizableStackWidget


def loadModules(path: str):
    sys.path.append(path)
    moduleloader.loadModulesFromPath(path)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.messageDB: Dict[str, MessageData] = {}

        self.DATA_PROVIDERS: Dict[str, IDataProvider] = {}
        self.GENERATORS: Dict[str, IGenerator] = {}

        self.data_provider_settings_stack: ResizableStackWidget = None
        self.combo_data_source: QComboBox = None
        self.generator_selection_box: QGroupBox = None
        self.generator_settings_tabs: QTabWidget = None

        self.line_out_path: QLineEdit = None
        self.btn_select_outpath: QToolButton = None

        self.messageView: MessageView = None

        self.btn_load_data: QToolButton = None
        self.btn_generate: QToolButton = None
        self.btn_select_all: QToolButton = None
        self.btn_select_none: QToolButton = None

        uic.loadUi('GUI/Windows/mainwindow.ui', self)

        setup_folder_select(self.btn_select_outpath, self.line_out_path)
        self.messageModel = self.setupMessageView()

        self.loadPlugins()
        self.loadDataProviders()
        self.loadGenerators()

        self.combo_data_source.currentIndexChanged.connect(self.onDataProviderCurrentChanged)

        self.btn_load_data.clicked.connect(self.onLoadData)
        self.btn_generate.clicked.connect(self.onGenerate)
        self.btn_select_all.clicked.connect(self.onSelectAll)
        self.btn_select_none.clicked.connect(self.onDeselectAll)


    def setupMessageView(self):
        model = MessageModel(0, 1, self)

        self.messageView.setModel(model)
        self.messageView.setUniformRowHeights(True)
        self.messageView.setHeaderHidden(True)
        self.messageView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.messageView.setItemDelegateForColumn(0, MessageWidget(self.messageView))

        return model

    def onLoadData(self):
        currentDataProviderName: str = self.combo_data_source.currentText()
        dataProvider = self.DATA_PROVIDERS[currentDataProviderName]
        messages = dataProvider.loadMessages(dataProvider.getUIWidget())

        for msg in messages:
            print(msg.getID())
            self.messageDB[msg.getID()] = msg

        self.messageModel.addMessages(messages)

    def onGenerate(self):
        try:
            self.btn_generate.setEnabled(False)

            messageData: List[MessageData] = self.getSelectedMessages()

            for generator in self.GENERATORS.values():
                if generator.enabled:
                    generator.generate(messageData, self.messageDB, self.line_out_path.text(), generator.getUIWidget())
        except Exception as ex:
            import traceback
            print(ex)
            traceback.print_exception(ex)
        finally:
            self.btn_generate.setEnabled(True)


    def getSelectedMessages(self):
        firstIndex = self.messageModel.index(0, 0, QModelIndex())
        messages: List[MessageData] = []
        for row in range(self.messageModel.rowCount(firstIndex.parent())):
            sibling = self.messageModel.index(row, firstIndex.column(), parent=firstIndex.parent())
            messages.extend(self.getSelectedMessagesFromChildren(sibling))

        return messages

    def getSelectedMessagesFromChildren(self, index: QModelIndex) -> List[MessageData]:
        checkState = index.data(Qt.ItemDataRole.CheckStateRole)
        if checkState == Qt.CheckState.Unchecked:
            return []

        messageData = index.data(DATA_ROLE_MESSAGE_DATA)
        if messageData is not None:
            return [messageData]

        messages = []
        for row in range(self.messageModel.rowCount(index)):
            child = self.messageModel.index(row, index.column(), parent=index)
            messages.extend(self.getSelectedMessagesFromChildren(child))

        return messages

    def onSelectAll(self):
        firstIndex = self.messageModel.index(0, 0, QModelIndex())
        for row in range(self.messageModel.rowCount(firstIndex.parent())):
            sibling = self.messageModel.index(row, firstIndex.column(), parent=firstIndex.parent())
            self.setCheckState(self.messageModel, sibling, Qt.CheckState.Checked)

    def onDeselectAll(self):
        firstIndex = self.messageModel.index(0, 0, QModelIndex())
        for row in range(self.messageModel.rowCount(firstIndex.parent())):
            sibling = self.messageModel.index(row, firstIndex.column(), parent=firstIndex.parent())
            self.setCheckState(self.messageModel, sibling, Qt.CheckState.Unchecked)

    def setCheckState(self, model: QAbstractItemModel, index: QModelIndex, state: Qt.CheckState):
        model.setData(index, state, Qt.ItemDataRole.CheckStateRole)

        self.setChildStates(model, index, state)
        self.setParentStates(model, index, state)

    def setChildStates(self, model: QAbstractItemModel, index: QModelIndex, state: Qt.CheckState):
        if model.hasChildren(index):
            for row in range(model.rowCount(index)):
                child = model.index(row, index.column(), parent=index)

                model.setData(child, state, Qt.ItemDataRole.CheckStateRole)
                self.setChildStates(model, child, state)

    def setParentStates(self, model: QAbstractItemModel, index: QModelIndex, state: Qt.CheckState):
        isStateConsistent: bool = True

        if not index.parent().isValid():
            return

        for row in range(model.rowCount(index.parent())):
            sibling = model.index(row, index.column(), parent=index.parent())

            if (sibling.data(Qt.ItemDataRole.CheckStateRole) != state):
                isStateConsistent = False

        if isStateConsistent:
            model.setData(index.parent(), state, Qt.ItemDataRole.CheckStateRole)
        else:
            model.setData(index.parent(), Qt.CheckState.PartiallyChecked, Qt.ItemDataRole.CheckStateRole)

        self.setParentStates(model, index.parent(), state)

    #region Plugins

    def onDataProviderCurrentChanged(self):
        self.data_provider_settings_stack.setCurrentIndex(self.combo_data_source.currentIndex())

    def loadPlugins(self):
        loadModules('plugins/')

    def loadDataProviders(self):
        data_providers = IDataProvider.__subclasses__()

        self.combo_data_source.clear()

        for provider in data_providers:
            instance = provider()
            self.DATA_PROVIDERS[instance.getName()] = instance
            self.combo_data_source.addItem(instance.getName())
            self.data_provider_settings_stack.addWidget(instance.getUIWidget())

        self.data_provider_settings_stack.setCurrentIndex(self.combo_data_source.currentIndex())

    def generateGeneratorCheckbox(self, generator: IGenerator) -> QAbstractButton:
        widget = QCheckBox()
        widget.setCheckable(True)
        widget.setChecked(True)
        widget.setText(generator.getLanguage())

        def cb():
            generator.enabled = widget.isChecked()

        widget.clicked.connect(cb)
        return widget

    def loadGenerators(self):
        generators = IGenerator.__subclasses__()

        generatorCount = 0

        for i in range(self.generator_selection_box.layout().count()):
            self.generator_selection_box.layout().itemAt(i).widget().deleteLater()

        for generator in generators:
            instance = generator()
            self.GENERATORS[instance.getLanguage()] = instance
            self.generator_selection_box.layout().addWidget(self.generateGeneratorCheckbox(instance),
                                                            generatorCount // COLUMNS_LANGUAGE_LAYOUT,
                                                            generatorCount % COLUMNS_LANGUAGE_LAYOUT)

            self.generator_settings_tabs.addTab(instance.getUIWidget(), instance.getLanguage())

            generatorCount += 1
    #endregion
