from app.extensions import db
from .base import TimestampMixin


class Inscripcion(TimestampMixin, db.Model):
    __tablename__ = "inscripciones"

    id = db.Column(db.Integer, primary_key=True)

    evento_id = db.Column(db.Integer, db.ForeignKey("eventos.id"), nullable=False, index=True)
    academia_id = db.Column(db.Integer, db.ForeignKey("academias.id"), nullable=False, index=True)

    evento = db.relationship("Evento", backref=db.backref("inscripciones", lazy=True))
    academia = db.relationship("Academia", backref=db.backref("inscripciones", lazy=True))

    estado = db.Column(db.String(20), default="BORRADOR", nullable=False)  # BORRADOR/ENVIADA/CONFIRMADA

    # Cantidad total declarada por la academia para el evento
    cantidad_participantes = db.Column(db.Integer, nullable=False, default=1)

    subtotal = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    descuentos = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    total = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    saldo = db.Column(db.Numeric(12, 2), default=0, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("evento_id", "academia_id", name="uq_inscripcion_evento_academia"),
    )


class InscripcionDetalle(TimestampMixin, db.Model):
    __tablename__ = "inscripcion_detalles"

    id = db.Column(db.Integer, primary_key=True)

    inscripcion_id = db.Column(db.Integer, db.ForeignKey("inscripciones.id"), nullable=False, index=True)
    tarifa_evento_id = db.Column(db.Integer, db.ForeignKey("tarifas_evento.id"), nullable=False, index=True)

    concepto = db.Column(db.String(120), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    valor_unitario = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    inscripcion = db.relationship(
        "Inscripcion",
        backref=db.backref("detalles", lazy=True, cascade="all, delete-orphan")
    )

    tarifa = db.relationship("TarifaEvento")

    __table_args__ = (
        db.UniqueConstraint(
            "inscripcion_id",
            "tarifa_evento_id",
            name="uq_detalle_inscripcion_tarifa",
        ),
    )