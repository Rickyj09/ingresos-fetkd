from app.extensions import db
from .base import TimestampMixin

class Pago(TimestampMixin, db.Model):
    __tablename__ = "pagos"
    id = db.Column(db.Integer, primary_key=True)

    inscripcion_id = db.Column(db.Integer, db.ForeignKey("inscripciones.id"), nullable=False, index=True)
    inscripcion = db.relationship("Inscripcion", backref=db.backref("pagos", lazy=True, cascade="all, delete-orphan"))

    fecha_pago = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Numeric(12,2), nullable=False)

    metodo = db.Column(db.String(30), nullable=True)
    referencia = db.Column(db.String(120), nullable=True)
    comprobante_path = db.Column(db.String(255), nullable=True)
    observacion = db.Column(db.String(255), nullable=True)