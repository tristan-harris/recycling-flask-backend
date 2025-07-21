from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user
from werkzeug.security import generate_password_hash

from . import RouteErrors, db_controller, get_resource, get_resource_all, create_resource, update_resource, delete_resource
from .other import other_routes_bp
from ..config import AppConfig
from ..database_controller import NotFoundError
from ..models import User, Submission, Purchase
from ..schemas import RegistrationSchema, validate_data

users_routes_bp = Blueprint("users", __name__, url_prefix= "/users")

@users_routes_bp.route("", methods=["POST"])
@other_routes_bp.route("register", methods=["POST"])
def create_user():
    request_data = request.get_json()

    validation_result = validate_data(request_data, RegistrationSchema)
    if not validation_result.valid:
        return {"error": validation_result.error_message, "message": validation_result.info}, 400
    request_data = validation_result.data

    # check if username or email are already taken
    if not db_controller.is_unique(User, "username", request_data["username"]):
        return {"error": "This username is already taken"}, 409
    if not db_controller.is_unique(User, "email", request_data["email"]):
        return {"error": "This email address has already been used"}, 409

    # check if user is of minimum age
    user_dob = request_data["date_of_birth"]
    today = date.today()
    cutoff = date(today.year - AppConfig.MINIMUM_AGE, today.month, today.day)

    # if user_dob is more recent (and therefore 'bigger'/longer than cutoff)
    if user_dob > cutoff:
        return {"error": f"You must be over the age of {AppConfig.MINIMUM_AGE}"}, 403

    request_data["password"] = generate_password_hash(request_data["password"])

    return create_resource(User, request_data, None)

@users_routes_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_user(id:int):
    if not db_controller.is_owner_or_moderator(current_user.id, User, id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    return get_resource(User, "id", id)

@users_routes_bp.route("", methods=["GET"])
@jwt_required()
def get_user_all():
    if not db_controller.has_moderator_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    return get_resource_all(User)

@users_routes_bp.route("/<int:id>/submissions", methods=["GET"])
@jwt_required()
def get_user_submissions(id:int):
    if not db_controller.is_owner_or_moderator(current_user.id, User, id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    try:
        db_controller.get(User, "id", id)
    except NotFoundError:
        return {"error": "User not found"}, 404
    else:
        submissions = db_controller.get_all_matching(Submission, "user_id", id)
        return {"submissions": [submission.to_dict() for submission in submissions]}

@users_routes_bp.route("/<int:id>/purchases", methods=["GET"])
@jwt_required()
def get_user_purchases(id:int):
    if not db_controller.is_owner_or_moderator(current_user.id, User, id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    try:
        db_controller.get(User, "id", id)
    except NotFoundError:
        return {"error": "User not found"}, 404
    else:
        purchases = db_controller.get_all_matching(Purchase, "user_id", id)
        return {"purchases": [purchase.to_dict() for purchase in purchases]}

@users_routes_bp.route("/<int:id>/balance", methods=["GET"])
@jwt_required()
def get_user_balance(id:int):
    if not db_controller.is_owner_or_moderator(current_user.id, User, id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    try:
        points_balance = db_controller.get_user_balance(id)
    except NotFoundError:
        return {"error": "User not found"}, 404
    else:
        return {"points_balance": points_balance}

@users_routes_bp.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def update_user(id:int):
    if not db_controller.is_owner_or_admin(current_user.id, User, id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    request_data = request.get_json()

    validation_result = validate_data(request_data, RegistrationSchema, partial=True)
    if not validation_result.valid:
        return {"error": validation_result.error_message, "message": validation_result.info}, 400
    request_data = validation_result.data

    if "password" in request_data:
        request_data["password"] = generate_password_hash(request_data["password"])

    return update_resource(User, "id", id, request_data, current_user.id)

@users_routes_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_user(id:int):
    if not db_controller.is_owner_or_admin(current_user.id, User, id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return delete_resource(User, "id", id, current_user.id)

@users_routes_bp.route("/<int:id>/freeze", methods=["POST"])
@jwt_required()
def freeze_user(id:int):
    if not db_controller.has_moderator_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    # prevent freezing of staff accounts
    if db_controller.has_moderator_access_level(id):
        return {"error": "Freezing a staff account is not allowed"}, 403

    return update_resource(User, "id", id, {"frozen": True}, current_user.id)

@users_routes_bp.route("/<int:id>/unfreeze", methods=["POST"])
@jwt_required()
def unfreeze_user(id:int):
    if not db_controller.has_moderator_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return update_resource(User, "id", id, {"frozen": False}, current_user.id)
