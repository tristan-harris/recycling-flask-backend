from flask import Blueprint, request, send_file, current_app
from flask_jwt_extended import jwt_required, current_user

from . import RouteErrors, db_controller, create_resource, get_resource, get_resource_all, \
    update_resource, delete_resource, NotFoundError

from ..constants import Constants
from ..models import Reward
from ..schemas import RewardSchema, validate_data
from ..util import get_image_upload_path, process_image, UnidentifiedImageError

rewards_routes_bp = Blueprint("rewards", __name__, url_prefix = "/rewards")

@rewards_routes_bp.route("", methods=["POST"])
@jwt_required()
def create_reward():
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    request_data = request.get_json()

    validation_result = validate_data(request_data, RewardSchema)
    if not validation_result.valid:
        return {"error": validation_result.error_message, "message": validation_result.info}, 400
    request_data = validation_result.data

    return create_resource(Reward, request_data, current_user.id)

@rewards_routes_bp.route("<int:id>/image", methods=["POST"])
@jwt_required()
def upload_reward_image(id:int):
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    try:
        db_controller.get(Reward, "id", id)
    except NotFoundError:
        return RouteErrors.NOT_FOUND.value

    image_path = get_image_upload_path(id, current_app.config["UPLOADS_DIRECTORY"], Constants.REWARD_IMAGES_DIRECTORY)

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

@rewards_routes_bp.route("/<int:id>", methods=["GET"])
def get_reward(id:int):
    return get_resource(Reward, "id", id)

@rewards_routes_bp.route("", methods=["GET"])
def get_reward_all():
    return get_resource_all(Reward)

@rewards_routes_bp.route("/<int:id>/image", methods=["GET"])
def get_reward_image(id:int):
    image_path = get_image_upload_path(id, current_app.config["UPLOADS_DIRECTORY"], Constants.REWARD_IMAGES_DIRECTORY)

    try:
        return send_file(image_path, mimetype="image/jpeg")
    except FileNotFoundError:
        return RouteErrors.NOT_FOUND.value
    except OSError:
        return RouteErrors.SERVER_ERROR.value

@rewards_routes_bp.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def update_reward(id:int):
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    request_data = request.get_json()

    validation_result = validate_data(request_data, RewardSchema, partial=True)
    if not validation_result.valid:
        return {"error": validation_result.error_message, "message": validation_result.info}, 400
    request_data = validation_result.data

    return update_resource(Reward, "id", id,  request_data, current_user.id)

@rewards_routes_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_reward(id:int):
    if not db_controller.has_admin_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return delete_resource(Reward, "id", id, current_user.id)
