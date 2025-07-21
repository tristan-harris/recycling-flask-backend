from enum import Enum


class StaffRole(Enum):
    moderator = "moderator"
    admin = "admin"


class SubmissionStatus(Enum):
    not_confirmed = "not_confirmed"
    confirmed = "confirmed"
    denied = "denied"
    # if AI is not confident in categorising image
    moderator_required = "moderator_required"


class ActionType(Enum):
    create = "create"
    read = "read"
    update = "update"
    delete = "delete"
