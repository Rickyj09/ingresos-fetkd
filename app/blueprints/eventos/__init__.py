from flask import Blueprint
bp = Blueprint("eventos", __name__, url_prefix="/eventos")
from . import routes  # noqa