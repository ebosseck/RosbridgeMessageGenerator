from PyQt6.QtWidgets import QWidget


class DummySettingsWidget(QWidget):

    def __init__(self, base_path: str, parent: QWidget = None):
        super(DummySettingsWidget, self).__init__(parent=parent)
