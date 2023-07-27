from typing import List, Dict, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from pytide_message_generator.dataprovider.message_data import MessageData
from pytide_message_generator.widgets.messageView.messagedatarole import DATA_ROLE_CATEGORY_DATA, DATA_ROLE_MESSAGE_DATA


class MessageModel(QStandardItemModel):

    def __init__(self, rows, columns, parent=None):
        super(MessageModel, self).__init__(rows, columns, parent)
        self.categorys: Dict[str, Tuple[dict, QStandardItem]] = {}
        self.messageDB: Dict[str, MessageData] = {}

    def addMessages(self, messages: List[MessageData]):
        root = self.invisibleRootItem()

        for message in messages:
            full_name = ".".join([*message.package, message.name])
            if full_name in self.messageDB:
                print("Ignored duplicate message: {}".format(full_name))
                continue

            self.messageDB[full_name] = message

            parent = root
            cats = self.categorys
            cname = ""
            for cat in message.package:
                cname += cat
                if cat not in cats:
                    catItem = QStandardItem(cat)
                    catItem.setCheckable(True)
                    cats[cat] = ({}, catItem)
                    catItem.setData({'name': cname}, role=DATA_ROLE_CATEGORY_DATA)
                    catItem.setSelectable(False)
                    parent.appendRow([catItem])
                cats, parent = cats[cat]
                cname += "."
            item = QStandardItem(message.name)
            item.setCheckable(True)

            item.setData(message, role=DATA_ROLE_MESSAGE_DATA)
            parent.appendRow([item])

        self.sort(0, Qt.SortOrder.AscendingOrder)