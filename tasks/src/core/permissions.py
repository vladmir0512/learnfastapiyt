from enum import Enum


class Permissions(Enum):
    VIEW_TASK = "view_task"
    UPDATE_TASK = "update_task"
    ADD_TASK = "add_task"
    DELETE_TASK = "delete_task"

    @classmethod
    def list(cls):
        return [permission.value for permission in cls]