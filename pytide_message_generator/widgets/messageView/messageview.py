from typing import Union

from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QPainter, QPalette, QColor
from PyQt6.QtWidgets import QTreeView, QStyleOptionViewItem

from pytide_message_generator.widgets.messageView.messagedatarole import DATA_ROLE_MESSAGE_DATA


class MessageView(QTreeView):

    def __init__(self, parent=None):
        super().__init__(parent)

    def startDrag(self, supportedActions: Qt.DropAction) -> None:
        super().startDrag(Qt.DropAction.CopyAction)

    def dragEnterEvent(self, event):
        event.ignore()

    def dragMoveEvent(self, event):
        event.ignore()

    def dropEvent(self, event):
        event.ignore()

    def drawRow(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        actionData = index.data(role=DATA_ROLE_MESSAGE_DATA)
        if actionData is not None:
            option.features = option.features & ~ option.ViewItemFeature.Alternate
        else:
            option.features = option.features | option.ViewItemFeature.Alternate
            option.palette.setBrush(QPalette.ColorRole.AlternateBase, option.palette.window())

        # Set Selection color to transparent
        option.palette.setColor(QPalette.ColorRole.Highlight, QColor("#00000000"))

        super(MessageView, self).drawRow(painter, option, index)