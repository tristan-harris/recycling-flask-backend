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
from ..database_controller import NotFoundError
from ..models import Purchase, Reward, User
from ..schemas import PurchaseSchema, validate_data

purchases_routes_bp = Blueprint("purchases", __name__, url_prefix="/purchases")


@purchases_routes_bp.route("", methods=["POST"])
@jwt_required()
def create_purchase():
    request_data = request.get_json()

    if "user_id" not in request_data or not isinstance(request_data["user_id"], int):
        return RouteErrors.INVALID_DATA.value

    if not db_controller.is_owner_or_admin(
        current_user.id, User, request_data["user_id"]
    ):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    if db_controller.is_frozen(current_user.id):
        return {
            "error": "Your account is frozen and you cannot make new purchases"
        }, 403

    validation_result = validate_data(request_data, PurchaseSchema)
    if not validation_result.valid:
        return {
            "error": validation_result.error_message,
            "message": validation_result.info,
        }, 400
    request_data = validation_result.data

    try:
        reward = db_controller.get(Reward, "id", request_data["reward_id"])
    except NotFoundError:
        return {"error": "Reward not found"}, 404

    try:
        user_balance = db_controller.get_user_balance(request_data["user_id"])
    except NotFoundError:
        return {"error": "User not found"}, 404

    # check if user can't afford reward
    if reward.price * request_data["quantity"] > user_balance:
        return {"error": "Insufficient points"}, 403

    return create_resource(Purchase, request_data, current_user.id)


@purchases_routes_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_purchase(id: int):
    if not db_controller.is_owner_or_moderator(current_user.id, Purchase, id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return get_resource(Purchase, "id", id)


@purchases_routes_bp.route("", methods=["GET"])
@jwt_required()
def get_purchase_all():
    if not db_controller.has_moderator_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return get_resource_all(Purchase)


@purchases_routes_bp.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def update_purchase(id: int):
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    request_data = request.get_json()

    validation_result = validate_data(request_data, PurchaseSchema, partial=True)
    if not validation_result.valid:
        return {
            "error": validation_result.error_message,
            "message": validation_result.info,
        }, 400
    request_data = validation_result.data

    return update_resource(Purchase, "id", id, request_data, current_user.id)


@purchases_routes_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_purchase(id: int):
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return delete_resource(Purchase, "id", id, current_user.id)
