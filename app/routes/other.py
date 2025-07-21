from flask import Blueprint, request
from flask_jwt_extended import create_access_token

from . import db_controller
from ..database_controller import NotFoundError, FailedAuthenticationError
from ..models import Staff
from ..schemas import LoginSchema, validate_data

other_routes_bp = Blueprint("other", __name__, url_prefix = "/")

@other_routes_bp.route("")
def home():
    message = "Recycling Project API"
    return {"message": message}

@other_routes_bp.route("login", methods=["POST"])
def login() -> dict | tuple[dict, int]:
    request_data = request.get_json()

    validation_result = validate_data(request_data, LoginSchema)
    if not validation_result.valid:
        return {"error": validation_result.error_message, "message": validation_result.info}, 400
    request_data = validation_result.data

    try:
        user = db_controller.validate_login(request_data)
    except (NotFoundError, FailedAuthenticationError):
        return {"error": "Authentication failed"}, 401

    return_data = {"message": "Login successful", "user": user.to_dict(),
                   "token": create_access_token(identity=user)}

    try:
        staff = db_controller.get(Staff, "user_id", user.id)
    except NotFoundError:
        return_data["role"] = "user"
    else:
        return_data["role"] = staff.role.value

    return return_data
