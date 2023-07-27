from PyQt6.QtCore import QModelIndex, Qt, QSize, QAbstractItemModel, QRect, QEvent
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QFont, QMouseEvent
from PyQt6.QtWidgets import QStyledItemDelegate, QTreeView, QStyleOptionViewItem, QWidget, QStylePainter, QStyle, \
    QStyleOptionButton, QStyleOption

from pytide_message_generator.dataprovider.message_data import MessageData
from pytide_message_generator.widgets.messageView.messagedatarole import DATA_ROLE_MESSAGE_DATA, DATA_ROLE_CATEGORY_DATA


class MessageWidget(QStyledItemDelegate):

    def __init__(self, view: QTreeView, parent=None):
        super(MessageWidget, self).__init__(parent)
        self.view: QTreeView = view

        self.brushCathegoryBg = QBrush(QColor(53, 53, 53, 75))
        self.brushActionBg = QBrush(QColor(25, 25, 25, 127))

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
        messageData: MessageData = index.data(role=DATA_ROLE_MESSAGE_DATA)
        if messageData is None:
            option.text = ""
        else:
            option.text = messageData.name
        option.displayAlignment = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft

    def sizeHint(self, option: QStyleOptionViewItem, modelIndex: QModelIndex):
        size: QSize = super(MessageWidget, self).sizeHint(option, modelIndex)
        size.setHeight(50)
        return size

    def editorEvent(self, event: QEvent, model: QAbstractItemModel,
                    option: 'QStyleOptionViewItem', index: QModelIndex) -> bool:

        if event.type() == QEvent.Type.MouseButtonPress:
            mouseEvent: QMouseEvent = event
            if mouseEvent.button() == Qt.MouseButton.LeftButton:
                checkboxRect = self.computeCheckboxRect(option)
                if checkboxRect.contains(mouseEvent.pos()):
                    self.updateCheckState(model, index)
                    event.setAccepted(True)
                    return True

        return super(MessageWidget, self).editorEvent(event, model, option, index)

    def updateCheckState(self, model: QAbstractItemModel, index: QModelIndex):
        state = index.data(Qt.ItemDataRole.CheckStateRole)
        if state == Qt.CheckState.Checked:
            self.setCheckState(model, index, Qt.CheckState.Unchecked)
        else:
            self.setCheckState(model, index, Qt.CheckState.Checked)


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

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        actionData = index.data(role=DATA_ROLE_MESSAGE_DATA)
        try:
            if actionData is not None:
                self.paintMessage(painter, option, index, actionData)
            else:
                self.paintCategory(painter, option, index, index.data())
            self.paintCheckbox(painter, option, index)
        except Exception as ex:
            print(ex)

    def paintMessage(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex, message: MessageData):
        x = option.rect.x()
        y = option.rect.y()
        w = option.rect.width()
        h = option.rect.height()

        painter.setBrush(self.brushActionBg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x, y, w, h)

        icon_offset = (h - 32) // 2

        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.setPen(QPen(Qt.GlobalColor.white))
        font: QFont = painter.font()
        font.setBold(False)
        font.setItalic(False)

        painter.setFont(font)

        text_offset = int(((h / 2)) // 2)

        painter.drawText(x + 32 + (icon_offset * 2), y + text_offset, w - (x + 32 + (icon_offset * 3)), 20, 0,
                         message.name)
        painter.setPen(QPen(Qt.GlobalColor.gray))
        font.setItalic(True)
        painter.setFont(font)
        painter.drawText(x + 32 + (icon_offset * 2), y + 15 + text_offset, w - (x + 32 + (icon_offset * 3)), 20, 0,
                         "{}".format(".".join(message.package)))
        font.setItalic(False)
        painter.setFont(font)

    def paintCategory(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex, category: str):
        categoryData = index.data(role=DATA_ROLE_CATEGORY_DATA)
        x = option.rect.x()
        y = option.rect.y()
        w = option.rect.width()
        h = option.rect.height()

        # painter.setBrush(self.brushCathegoryBg)
        painter.setPen(Qt.PenStyle.NoPen)
        # painter.drawRect(x, y, w, h)

        icon_offset = (h - 32) // 2

        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.setPen(QPen(Qt.GlobalColor.white))
        font: QFont = painter.font()
        font.setBold(True)
        painter.setFont(font)
        text_offset = (h - 12) // 2

        painter.drawText(x + 32 + (icon_offset * 2), y + text_offset, w - (x + 32 + (icon_offset * 3)), 20, 0, category)
        font.setBold(False)
        painter.setFont(font)

    def paintCheckbox(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        style: QStyle = option.widget.style()
        checkboxOption = QStyleOptionButton()

        checkboxOption.rect = self.computeCheckboxRect(option)

        checkState = index.data(Qt.ItemDataRole.CheckStateRole)

        if (checkState == Qt.CheckState.Checked):
            checkboxOption.state = QStyle.StateFlag.State_On
        elif (checkState == Qt.CheckState.PartiallyChecked):
            checkboxOption.state = QStyle.StateFlag.State_NoChange | QStyle.StateFlag.State_On
        else:
            checkboxOption.state = QStyle.StateFlag.State_Off

        style.drawControl(QStyle.ControlElement.CE_CheckBox, checkboxOption, painter)

    def computeCheckboxRect(self, option: QStyleOption):
        x = option.rect.x()
        y = option.rect.y()

        w = option.rect.width()
        h = option.rect.height()

        checkboxOption_offset = (h - 20) // 2

        return QRect(x + checkboxOption_offset, y + checkboxOption_offset, 20, 20)

    def createEditor(self, widget, style, index):
        return None

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex):
        print("Setting Model Data")
