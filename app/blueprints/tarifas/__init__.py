from flask import Blueprint
bp = Blueprint("tarifas", __name__, url_prefix="/tarifas")
from . import routes  # noqa