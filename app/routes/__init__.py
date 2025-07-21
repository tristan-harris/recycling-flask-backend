from enum import Enum

from ..database_controller import DatabaseController, InvalidDataError, NotFoundError, ServerError
from ..jwt import jwt_manager
from ..models import User

class RouteErrors(Enum):
    INVALID_DATA = ({"error": "Invalid data"}, 400)
    UNAUTHORISED_ACCESS = ({"error": "Unauthorised access"}, 403)
    NOT_FOUND = ({"error": "Resource not found"}, 404)

    MISSING_IMAGE = ({"error": "No image uploaded"}, 400)
    IMAGE_PROCESSING_ERROR = ({"error": "Image could not be processed"}, 500)

    SERVER_ERROR = ({"error": "Unexpected server error"}, 500)

db_controller = DatabaseController()

def create_resource(model, request_data:dict, current_user_id:int|None) -> dict | tuple[dict, int]:
    try:
        resource = db_controller.create_new(model, request_data, current_user_id)
    except InvalidDataError:
        return RouteErrors.INVALID_DATA.value
    except ServerError:
        return RouteErrors.SERVER_ERROR.value

    return {"message": "Resource created", "resource": resource.to_dict()}, 201

def get_resource(model, key:str, value) -> dict | tuple[dict, int]:
    try:
        resource = db_controller.get(model, key, value)
    except NotFoundError:
        return RouteErrors.NOT_FOUND.value

    return resource.to_dict()

def get_resource_all(model) -> dict:
    resources = db_controller.get_all(model)
    return {f"{model.__tablename__}": [resource.to_dict() for resource in resources]}

def update_resource(model, key:str, value, request_data:dict, current_user_id:int) -> dict | tuple[dict, int]:
    try:
        db_controller.update(model, key, value, request_data, current_user_id)
    except NotFoundError:
        return RouteErrors.NOT_FOUND.value
    except InvalidDataError:
        return RouteErrors.INVALID_DATA.value
    except ServerError:
        return RouteErrors.SERVER_ERROR.value

    return {"message": f"{model.__tablename__} record updated"}

def delete_resource(model, key:str, value, current_user_id:int) -> dict | tuple[dict, int]:
    try:
        db_controller.delete(model, key, value, current_user_id)
    except NotFoundError:
        return RouteErrors.NOT_FOUND.value

    return {"message": "Resource deleted"}

@jwt_manager.user_identity_loader
def user_identity_lookup(user):
    return str(user.id)

@jwt_manager.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = int(jwt_data["sub"])
    return User.query.filter_by(id=identity).one_or_none() # TODO update

from .bins import bins_routes_bp
from .logs import log_routes_bp
from .motivations import motivations_routes_bp
from .other import other_routes_bp
from .purchases import purchases_routes_bp
from .recyclables import recyclables_routes_bp
from .rewards import rewards_routes_bp
from .staff import staff_routes_bp
from .statistics import statistics_routes_bp
from .submissions import submissions_routes_bp
from .users import users_routes_bp

route_blueprints = [
    bins_routes_bp,
    log_routes_bp,
    motivations_routes_bp,
    other_routes_bp,
    purchases_routes_bp,
    recyclables_routes_bp,
    rewards_routes_bp,
    staff_routes_bp,
    statistics_routes_bp,
    submissions_routes_bp,
    users_routes_bp,
]
