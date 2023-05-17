from PyQt6.QtWidgets import QToolButton, QLineEdit, QFileDialog


def setup_folder_select(btn: QToolButton, lineedit: QLineEdit):
    def btn_click():
        path = QFileDialog.getExistingDirectory(None, "Open Directory", lineedit.text())
        lineedit.setText(path)

    btn.clicked.connect(btn_click)