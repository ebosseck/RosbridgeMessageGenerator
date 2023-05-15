from typing import Optional


class FieldData:
    def __init__(self, field_type: str, field_name: str,
                 is_array: bool = False, array_fixed_length: int = -1, max_array_size: int = -1,
                 constant_value: Optional[str]=None):
        self.field_type: str = field_type
        self.field_name: str = field_name
        self.is_array: bool = is_array
        self.array_fixed_length: array_fixed_length = array_fixed_length
        self.max_array_size: max_array_size = max_array_size
        self.constant_value: constant_value = constant_value