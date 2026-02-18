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

    subtotal = db.Column(db.Numeric(12,2), default=0, nullable=False)
    descuentos = db.Column(db.Numeric(12,2), default=0, nullable=False)
    total = db.Column(db.Numeric(12,2), default=0, nullable=False)
    saldo = db.Column(db.Numeric(12,2), default=0, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("evento_id", "academia_id", name="uq_inscripcion_evento_academia"),
    )

class InscripcionDetalle(TimestampMixin, db.Model):
    """
    Un 'detalle' representa un bloque agregado:
    (modalidad + [categoria/division/dan]) con cantidad y precio unitario.
    NO hay personas, solo cantidades.
    """
    __tablename__ = "inscripcion_detalles"
    id = db.Column(db.Integer, primary_key=True)

    inscripcion_id = db.Column(db.Integer, db.ForeignKey("inscripciones.id"), nullable=False, index=True)
    inscripcion = db.relationship(
        "Inscripcion",
        backref=db.backref("detalles", lazy=True, cascade="all, delete-orphan")
    )

    modalidad = db.Column(db.String(20), nullable=False)  # COMBATE/POOMSAE/PARA_TKD

    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias_competencia.id"), nullable=True, index=True)
    division_poomsae_id = db.Column(db.Integer, db.ForeignKey("divisiones_poomsae.id"), nullable=True, index=True)
    dan_nivel = db.Column(db.Integer, nullable=True)

    cantidad = db.Column(db.Integer, nullable=False)
    valor_unitario = db.Column(db.Numeric(10,2), nullable=False)
    total = db.Column(db.Numeric(12,2), nullable=False)

    __table_args__ = (
        # Evita duplicar la misma “línea” para una inscripción
        db.UniqueConstraint(
            "inscripcion_id", "modalidad", "categoria_id", "division_poomsae_id", "dan_nivel",
            name="uq_detalle_inscripcion_dimensiones"
        ),
    )