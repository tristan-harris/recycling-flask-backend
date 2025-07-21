from flask import Blueprint

from . import db_controller
from ..models import Submission

statistics_routes_bp = Blueprint("statistics", __name__, url_prefix="/statistics")


@statistics_routes_bp.route("", methods=["GET"])
def get_statistics():
    return {"total_submissions": db_controller.get_count_of(Submission)}
