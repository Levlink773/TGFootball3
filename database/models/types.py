from enum import Enum

class TypeBox(str, Enum):
    SMALL_BOX = "small_box"
    MEDIUM_BOX = "medium_box"
    LARGE_BOX = "large_box"
    NEW_MEMBER_BOX = "new_member_box"