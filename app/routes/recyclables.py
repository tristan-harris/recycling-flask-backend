from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user

from . import RouteErrors, db_controller, create_resource, get_resource, get_resource_all, \
    update_resource, delete_resource
from ..models import Recyclable
from ..schemas import RecyclableSchema, validate_data

recyclables_routes_bp = Blueprint("recyclables", __name__, url_prefix = "/recyclables")

@recyclables_routes_bp.route("", methods=["POST"])
@jwt_required()
def create_recyclable():
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    request_data = request.get_json()

    validation_result = validate_data(request_data, RecyclableSchema)
    if not validation_result.valid:
        return {"error": validation_result.error_message, "message": validation_result.info}, 400
    request_data = validation_result.data

    return create_resource(Recyclable, request_data, current_user.id)

@recyclables_routes_bp.route("/<int:id>", methods=["GET"])
def get_recyclable(id:int):
    return get_resource(Recyclable, "id", id)

@recyclables_routes_bp.route("", methods=["GET"])
def get_recyclable_all():
    return get_resource_all(Recyclable)

@recyclables_routes_bp.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def update_recyclable(id:int):
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    request_data = request.get_json()

    validation_result = validate_data(request_data, RecyclableSchema, partial=True)
    if not validation_result.valid:
        return {"error": validation_result.error_message, "message": validation_result.info}, 400
    request_data = validation_result.data

    return update_resource(Recyclable, "id", id, request_data, current_user.id)

@recyclables_routes_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_recyclable(id:int):
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return delete_resource(Recyclable, "id", id, current_user.id)
