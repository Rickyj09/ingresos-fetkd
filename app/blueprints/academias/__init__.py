from flask import Blueprint
bp = Blueprint("academias", __name__, url_prefix="/academias")
from . import routes  # noqa