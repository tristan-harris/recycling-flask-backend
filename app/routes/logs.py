from flask import Blueprint
from flask_jwt_extended import jwt_required, current_user

from . import RouteErrors, db_controller, get_resource, get_resource_all

from ..models import UserActionLog

log_routes_bp = Blueprint("logs", __name__, url_prefix="/logs")


@log_routes_bp.route("/actions/<int:id>", methods=["GET"])
@jwt_required()
def get_action_log(id: int):
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return get_resource(UserActionLog, "id", id)


@log_routes_bp.route("/actions", methods=["GET"])
@jwt_required()
def get_action_log_all():
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return get_resource_all(UserActionLog)
