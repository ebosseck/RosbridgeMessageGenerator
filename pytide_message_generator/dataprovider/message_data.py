from typing import List

from pytide_message_generator.dataprovider.field_data import FieldData


class MessageData:

    def __init__(self, package: List[str], name: str, fields: List[FieldData],
                 srv_siblings: List['MessageData'] = None, srv_name: str = None):
        self.package: List[str] = package
        self.name: str = name
        self.fields: List[FieldData] = fields

        self.srv_siblings = srv_siblings
        self.srv_name = srv_name
        self.srv_index = 0

    @property
    def isService(self):
        return self.srv_siblings is not None

    def getID (self):
        return "/".join([*self.package, self.name])