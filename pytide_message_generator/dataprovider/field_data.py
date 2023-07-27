from typing import Optional, Union


class FieldData:
    def __init__(self, field_type: str, field_name: str,
                 is_array: bool = False, array_fixed_length: int = -1, max_array_size: int = -1,
                 constant_value: Optional[Union[str, bool, int, float]] = None, comment: str = ""):
        self.field_type: str = field_type
        self.field_name: str = field_name
        self.is_array: bool = is_array
        self.array_fixed_length: int = array_fixed_length
        self.max_array_size: int = max_array_size
        self.constant_value: Optional[Union[str, bool, int, float]] = constant_value
        self.comment: str = comment
