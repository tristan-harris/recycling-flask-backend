from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user

from . import (
    RouteErrors,
    db_controller,
    create_resource,
    get_resource,
    get_resource_all,
    update_resource,
    delete_resource,
)
from ..models import Motivation, User
from ..schemas import MotivationSchema, validate_data

motivations_routes_bp = Blueprint("motivation", __name__, url_prefix="/motivations")


@motivations_routes_bp.route("", methods=["POST"])
@jwt_required()
def create_motivation():
    request_data = request.get_json()

    if "user_id" not in request_data or not isinstance(request_data["user_id"], int):
        return RouteErrors.INVALID_DATA.value

    if not db_controller.is_owner_or_admin(
        current_user.id, User, request_data["user_id"]
    ):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    validation_result = validate_data(request_data, MotivationSchema)
    if not validation_result.valid:
        return {
            "error": validation_result.error_message,
            "message": validation_result.info,
        }, 400
    request_data = validation_result.data

    return create_resource(Motivation, request_data, current_user.id)


@motivations_routes_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_motivation(user_id: int):
    if not db_controller.has_moderator_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    return get_resource(Motivation, "user_id", user_id)


@motivations_routes_bp.route("", methods=["GET"])
@jwt_required()
def get_motivation_all():
    if not db_controller.has_moderator_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return get_resource_all(Motivation)


@motivations_routes_bp.route("/<int:user_id>", methods=["PATCH"])
@jwt_required()
def update_motivation(user_id: int):
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    request_data = request.get_json()

    validation_result = validate_data(request_data, MotivationSchema, partial=True)
    if not validation_result.valid:
        return {
            "error": validation_result.error_message,
            "message": validation_result.info,
        }, 400
    request_data = validation_result.data

    return update_resource(
        Motivation, "user_id", user_id, request_data, current_user.id
    )


@motivations_routes_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_motivation(user_id: int):
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    return delete_resource(Motivation, "user_id", user_id, current_user.id)
