import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QComboBox, QGroupBox, QAbstractButton, QToolButton, QCheckBox, QTabWidget, \
    QLineEdit, QPushButton

from pytide_message_generator.dataprovider.idataprovider import IDataProvider
from pytide_message_generator.generator.igenerator import IGenerator
from pytide_message_generator.plugin import moduleloader
from pytide_message_generator.settings.settings import COLUMNS_LANGUAGE_LAYOUT
from pytide_message_generator.tools.ui_interaction_tools import setup_folder_select
from pytide_message_generator.widgets.resizeablestackwidget import ResizableStackWidget


def loadModules(path: str):
    sys.path.append(path)
    moduleloader.loadModulesFromPath(path)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.DATA_PROVIDERS = {}
        self.GENERATORS = {}

        self.data_provider_settings_stack: ResizableStackWidget = None
        self.combo_data_source: QComboBox = None
        self.generator_selection_box: QGroupBox = None
        self.generator_settings_tabs: QTabWidget = None

        self.line_out_path: QLineEdit = None
        self.btn_select_outpath: QToolButton = None

        self.btn_load_data: QToolButton = None
        self.btn_generate: QToolButton = None
        self.btn_select_all: QToolButton = None
        self.btn_select_none: QToolButton = None


        uic.loadUi('GUI/Windows/mainwindow.ui', self)

        setup_folder_select(self.btn_select_outpath, self.line_out_path)

        self.loadPlugins()
        self.loadDataProviders()
        self.loadGenerators()

        self.combo_data_source.currentIndexChanged.connect(self.onDataProviderCurrentChanged)

        self.btn_load_data.clicked.connect(self.onLoadData)
        self.btn_generate.clicked.connect(self.onGenerate)
        self.btn_select_all.clicked.connect(self.onSelectAll)
        self.btn_select_none.clicked.connect(self.onDeselectAll)


    def onLoadData(self):
        pass

    def onGenerate(self):
        pass

    def onSelectAll(self):
        pass

    def onDeselectAll(self):
        pass

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