from app.extensions import db
from .base import TimestampMixin


class RubroEgreso(TimestampMixin, db.Model):
    __tablename__ = "rubros_egreso"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(120), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)

class EgresoEvento(TimestampMixin, db.Model):
    __tablename__ = "egresos_evento"

    id = db.Column(db.Integer, primary_key=True)

    evento_id = db.Column(db.Integer, db.ForeignKey("eventos.id"), nullable=False, index=True)
    rubro_egreso_id = db.Column(db.Integer, db.ForeignKey("rubros_egreso.id"), nullable=False, index=True)

    fecha = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    proveedor = db.Column(db.String(150), nullable=True)

    valor = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    numero_comprobante = db.Column(db.String(80), nullable=True)
    comprobante_path = db.Column(db.String(255), nullable=True)
    observacion = db.Column(db.String(255), nullable=True)

    evento = db.relationship("Evento", backref=db.backref("egresos", lazy=True, cascade="all, delete-orphan"))
    rubro = db.relationship("RubroEgreso", backref=db.backref("egresos", lazy=True))