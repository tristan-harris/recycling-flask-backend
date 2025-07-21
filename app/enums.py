from enum import Enum

class StaffRole(Enum):
    moderator           = "moderator"
    admin               = "admin"

class SubmissionStatus(Enum):
    not_confirmed       = "not_confirmed"
    confirmed           = "confirmed"
    denied              = "denied"
    moderator_required  = "moderator_required" # if AI is not confident in categorising image

class ActionType(Enum):
    create              = "create"
    read                = "read"
    update              = "update"
    delete              = "delete"