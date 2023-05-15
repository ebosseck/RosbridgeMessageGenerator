from typing import List

from pytide_message_generator.dataprovider.field_data import FieldData


class MessageData:

    def __init__(self, package: str, name: str, fields: List[FieldData]):
        self.package: str = package
        self.name: str = name
        self.fields: str = fields
