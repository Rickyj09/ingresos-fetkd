from app.extensions import db
from .base import TimestampMixin


class InscripcionEventoDetalle(TimestampMixin, db.Model):
    __tablename__ = "inscripciones_evento_detalle"

    id = db.Column(db.Integer, primary_key=True)

    inscripcion_id = db.Column(
        db.Integer,
        db.ForeignKey("inscripciones_evento.id"),
        nullable=False,
        index=True
    )

    tarifa_evento_id = db.Column(
        db.Integer,
        db.ForeignKey("tarifas_evento.id"),
        nullable=False,
        index=True
    )

    cantidad = db.Column(db.Integer, nullable=False, default=0)

    valor_unitario = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    tarifa = db.relationship("TarifaEvento")