from flask import Blueprint

bp = Blueprint("inscripciones", __name__, url_prefix="/inscripciones")

from . import routes  # noqa