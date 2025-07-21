from flask import Blueprint, request, send_file, current_app
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

from ..constants import Constants
from ..database_controller import NotFoundError
from ..models import Bin
from ..schemas import BinSchema, validate_data
from ..util import get_image_upload_path, process_image, UnidentifiedImageError

bins_routes_bp = Blueprint("bins", __name__, url_prefix="/bins")


@bins_routes_bp.route("", methods=["POST"])
@jwt_required()
def create_bin():
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    request_data = request.get_json()

    validation_result = validate_data(request_data, BinSchema)
    if not validation_result.valid:
        return {
            "error": validation_result.error_message,
            "message": validation_result.info,
        }, 400
    request_data = validation_result.data

    return create_resource(Bin, request_data, current_user.id)


@bins_routes_bp.route("<int:id>/image", methods=["POST"])
@jwt_required()
def upload_bin_image(id: int):
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    # check if bin exists
    try:
        db_controller.get(Bin, "id", id)
    except NotFoundError:
        return RouteErrors.NOT_FOUND.value

    image_path = get_image_upload_path(
        id, current_app.config["UPLOADS_DIRECTORY"], Constants.BIN_IMAGES_DIRECTORY
    )

    if "image" not in request.files:
        return RouteErrors.MISSING_IMAGE.value

    image_file = request.files["image"]

    try:
        process_image(image_file, image_path)
    except UnidentifiedImageError:
        return RouteErrors.IMAGE_PROCESSING_ERROR.value
    except OSError:
        return RouteErrors.IMAGE_PROCESSING_ERROR.value

    return {"message": "Image uploaded, verification pending."}


@bins_routes_bp.route("/<int:id>", methods=["GET"])
def get_bin(id: int):
    return get_resource(Bin, "id", id)


@bins_routes_bp.route("", methods=["GET"])
def get_bin_all():
    return get_resource_all(Bin)


@bins_routes_bp.route("/<int:id>/image", methods=["GET"])
def get_bin_image(id: int):
    image_path = get_image_upload_path(
        id, current_app.config["UPLOADS_DIRECTORY"], Constants.BIN_IMAGES_DIRECTORY
    )

    try:
        return send_file(image_path, mimetype="image/jpeg")
    except FileNotFoundError:
        return RouteErrors.NOT_FOUND.value
    except OSError:
        return RouteErrors.SERVER_ERROR.value


@bins_routes_bp.route("/<int:id>/whitelist", methods=["GET"])
def get_bin_whitelist(id: int):
    try:
        bin = db_controller.get(Bin, "id", id)
    except NotFoundError:
        return RouteErrors.NOT_FOUND.value

    # no need to get whitelisted recyclables if no whitelist
    if not bin.whitelist:
        return {"whitelist": False, "message": f"Bin {id} does not have a whitelist"}

    recyclables = db_controller.get_bin_whitelist(id)
    return {
        "whitelist": True,
        "recyclables": [recyclable.to_dict() for recyclable in recyclables],
    }


@bins_routes_bp.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def update_bin(id: int):
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    request_data = request.get_json()

    validation_result = validate_data(request_data, BinSchema, partial=True)
    if not validation_result.valid:
        return {
            "error": validation_result.error_message,
            "message": validation_result.info,
        }, 400
    request_data = validation_result.data

    return update_resource(Bin, "id", id, request_data, current_user.id)


@bins_routes_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_bin(id: int):
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return delete_resource(Bin, "id", id, current_user.id)
