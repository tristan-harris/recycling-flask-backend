from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user

from . import RouteErrors, db_controller, create_resource, get_resource, get_resource_all, update_resource, delete_resource
from ..models import Staff
from ..schemas import StaffSchema, validate_data

staff_routes_bp = Blueprint("staff", __name__, url_prefix= "/staff")

@staff_routes_bp.route("", methods=["POST"])
@jwt_required()
def create_staff():
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    request_data = request.get_json()

    validation_result = validate_data(request_data, StaffSchema)
    if not validation_result.valid:
        return {"error": validation_result.error_message, "message": validation_result.info}, 400
    request_data = validation_result.data

    return create_resource(Staff, request_data, current_user.id)

@staff_routes_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_staff(user_id:int):
    if not db_controller.has_moderator_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return get_resource(Staff, "user_id", user_id)

@staff_routes_bp.route("", methods=["GET"])
@jwt_required()
def get_staff_all():
    if not db_controller.has_moderator_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return get_resource_all(Staff)

@staff_routes_bp.route("/<int:user_id>", methods=["PATCH"])
@jwt_required()
def update_staff(user_id:int):
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    request_data = request.get_json()

    validation_result = validate_data(request_data, StaffSchema, partial=True)
    if not validation_result.valid:
        return {"error": validation_result.error_message, "message": validation_result.info}, 400
    request_data = validation_result.data

    return update_resource(Staff, "user_id", user_id, request_data, current_user.id)

@staff_routes_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_staff(user_id:int):
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    return delete_resource(Staff, "user_id", user_id, current_user.id)
