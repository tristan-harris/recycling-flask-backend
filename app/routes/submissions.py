from flask import Blueprint, request, send_file, current_app
from flask_jwt_extended import jwt_required, current_user
from haversine import haversine, Unit

from . import (
    RouteErrors,
    db_controller,
    create_resource,
    get_resource,
    get_resource_all,
    update_resource,
    delete_resource,
)
from ..config import AppConfig
from ..constants import Constants
from ..database_controller import NotFoundError
from ..models import Bin, Submission, User
from ..schemas import SubmissionCreationSchema, SubmissionUpdateSchema, validate_data
from ..util import get_image_upload_path, process_image, UnidentifiedImageError

submissions_routes_bp = Blueprint("submissions", __name__, url_prefix="/submissions")


@submissions_routes_bp.route("", methods=["POST"])
@jwt_required()
def create_submission():
    request_data = request.get_json()

    if "user_id" not in request_data or not isinstance(request_data["user_id"], int):
        return RouteErrors.INVALID_DATA.value

    if not db_controller.is_owner_or_admin(
        current_user.id, User, request_data["user_id"]
    ):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    if db_controller.is_frozen(current_user.id):
        return {
            "error": "Your account is frozen and you cannot make new submissions"
        }, 403

    validation_result = validate_data(request_data, SubmissionCreationSchema)
    if not validation_result.valid:
        return {
            "error": validation_result.error_message,
            "message": validation_result.info,
        }, 400
    request_data = validation_result.data

    try:
        bin = db_controller.get(Bin, "id", request_data["bin_id"])
    except NotFoundError:
        return {"error": "Bin not found"}, 404

    # if bin has a restricted list of valid recyclables
    # check that submitted recyclable is one of them
    if bin.whitelist:
        whitelisted_recyclables = db_controller.get_bin_whitelist(
            request_data["bin_id"]
        )
        whitelisted = False
        for recyclable in whitelisted_recyclables:
            if recyclable.id == request_data["recyclable_id"]:
                whitelisted = True
                break

        if not whitelisted:
            return {"error": "Recyclable not allowed for this bin"}, 403

    # check distance from bin being submitted to
    distance = haversine(
        (request_data["latitude"], request_data["longitude"]),
        (bin.latitude, bin.longitude),
        unit=Unit.METERS,
    )
    if distance > AppConfig.MAX_BIN_DISTANCE:
        return {"error": "Not within sufficient distance of specified bin"}, 403

    return create_resource(Submission, request_data, current_user.id)


@submissions_routes_bp.route("<int:id>/image", methods=["POST"])
@jwt_required()
def upload_submission_image(id: int):
    # also checks if submission exists
    if not db_controller.is_owner_or_admin(current_user.id, Submission, id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    image_path = get_image_upload_path(
        id,
        current_app.config["UPLOADS_DIRECTORY"],
        Constants.SUBMISSION_IMAGES_DIRECTORY,
    )

    if image_path.exists():
        return {"error": "Submission image already exists"}, 400

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


@submissions_routes_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_submission(id: int):
    if not db_controller.has_moderator_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return get_resource(Submission, "id", id)


@submissions_routes_bp.route("", methods=["GET"])
@jwt_required()
def get_submission_all():
    if not db_controller.has_moderator_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return get_resource_all(Submission)


@submissions_routes_bp.route("/<int:id>/image", methods=["GET"])
@jwt_required()
def get_submission_image(id: int):
    if not db_controller.is_owner_or_moderator(current_user.id, Submission, id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    image_path = get_image_upload_path(
        id,
        current_app.config["UPLOADS_DIRECTORY"],
        Constants.SUBMISSION_IMAGES_DIRECTORY,
    )

    try:
        return send_file(image_path, mimetype="image/jpeg")
    except FileNotFoundError:
        return RouteErrors.NOT_FOUND.value
    except OSError:
        return RouteErrors.SERVER_ERROR.value


@submissions_routes_bp.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def update_submission(id: int):
    if not db_controller.has_moderator_access_level(current_user.id):
        return RouteErrors.UNAUTHORISED_ACCESS.value

    request_data = request.get_json()

    validation_result = validate_data(
        request_data, SubmissionUpdateSchema, partial=True
    )
    if not validation_result.valid:
        return {
            "error": validation_result.error_message,
            "message": validation_result.info,
        }, 400
    request_data = validation_result.data

    return update_resource(Submission, "id", id, request_data, current_user.id)


@submissions_routes_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_submission(id: int):
    if not db_controller.is_owner_or_moderator(current_user.id, Submission, id):
        return RouteErrors.UNAUTHORISED_ACCESS.value
    return delete_resource(Submission, "id", id, current_user.id)
