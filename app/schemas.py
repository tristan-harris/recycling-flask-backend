'''Schemas for validating JSON input'''

from marshmallow import Schema, ValidationError, fields, validate, validates_schema

from .enums import StaffRole, SubmissionStatus

_roles = [role.value for role in StaffRole]
_statuses = [status.value for status in SubmissionStatus]

class RegistrationSchema(Schema):
    username        = fields.Str(required = True, validate = validate.Length(max=255))
    password        = fields.Str(required = True, validate = validate.Length(max=255))
    email           = fields.Email(required = True, validate = validate.Length(max=320))
    phone_number    = fields.Str(validate = validate.Length(max=15))
    first_name      = fields.Str(validate = validate.Length(max=255))
    last_name       = fields.Str(validate = validate.Length(max=255))
    date_of_birth   = fields.Date(required = True)
    organisation    = fields.Str(validate = validate.Length(max=255))

class LoginSchema(Schema):
    username        = fields.Str(required = False)
    email           = fields.Str(required = False)
    password        = fields.Str(required = True)

    @validates_schema
    def validate_username_or_email(self, data, **kwargs):
        if data.get('username') and data.get('email'):
            raise ValidationError("Cannot send both username and email", field_name='username')
        if not data.get('username') and not data.get('email'):
            raise ValidationError("Either username or email is required.", field_name='username')

class MotivationSchema(Schema):
    user_id         = fields.Int(required = True)
    motivation      = fields.Str(required = True, validate = validate.Length(max=2000))

class StaffSchema(Schema):
    user_id         = fields.Int(required = True)
    role            = fields.Str(validate = validate.OneOf(_roles), required = True)

class BinSchema(Schema):
    latitude        = fields.Float(required = True)
    longitude       = fields.Float(required = True)
    name            = fields.Str(validate = validate.Length(max=200))
    description     = fields.Str(validate = validate.Length(max=2000))

class RecyclableSchema(Schema):
    type            = fields.Str(required = True)
    points_value    = fields.Int(required = True)
    description     = fields.Str(validate = validate.Length(max=500))
    weight          = fields.Float()

class SubmissionCreationSchema(Schema):
    recyclable_id   = fields.Int(required = True)
    user_id         = fields.Int(required = True)
    bin_id          = fields.Int(required = True)
    latitude        = fields.Float(required = True)
    longitude       = fields.Float(required = True)

class SubmissionUpdateSchema(Schema):
    recyclable_id   = fields.Int()
    user_id         = fields.Int()
    bin_id          = fields.Int()
    status          = fields.Str(validate = validate.OneOf(_statuses))

class RewardSchema(Schema):
    title           = fields.Str(required = True)
    description     = fields.Str(validate = validate.Length(max=2000))
    price           = fields.Int(required = True)

class PurchaseSchema(Schema):
    user_id         = fields.Int(required = True)
    reward_id       = fields.Int(required = True)
    quantity        = fields.Int()

class ValidationResult():
    def __init__(self) -> None:
        self.valid:bool = False
        self.error_message:str = "Invalid data"
        self.info:dict = {}
        self.data:dict = {}

def validate_data(data:dict, schema, partial:bool = False) -> ValidationResult:
    validation_result = ValidationResult()
    try:
        # missing fields ignored if partial = True
        validation_result.data = schema().load(data, partial = partial)
    except ValidationError as e:
        validation_result.info = e.messages_dict
        return validation_result

    validation_result.valid = True
    return validation_result
