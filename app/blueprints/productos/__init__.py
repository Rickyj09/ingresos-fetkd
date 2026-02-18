from flask import Blueprint
bp = Blueprint("productos", __name__, url_prefix="/productos")
from . import routes  # noqa