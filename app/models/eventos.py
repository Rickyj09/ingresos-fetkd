from app.extensions import db
from .base import TimestampMixin


class Evento(TimestampMixin, db.Model):
    __tablename__ = "eventos"

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos_servicio.id"), nullable=False, index=True)

    nombre = db.Column(db.String(190), nullable=False)
    anio = db.Column(db.Integer, nullable=False, index=True)
    sede = db.Column(db.String(150), nullable=True)

    fecha_inicio = db.Column(db.Date, nullable=True)
    fecha_fin = db.Column(db.Date, nullable=True)

    estado = db.Column(db.String(20), nullable=False, default="BORRADOR")

    # NUEVO: valor base del evento
    valor_base = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    producto = db.relationship("ProductoServicio", backref=db.backref("eventos", lazy=True))


class TarifaEvento(TimestampMixin, db.Model):
    __tablename__ = "tarifas_evento"

    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey("eventos.id"), nullable=False, index=True)

    nombre = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    valor = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    evento = db.relationship(
        "Evento",
        backref=db.backref("tarifas", lazy=True, cascade="all, delete-orphan")
    )

class TarifaEventoDetalle(TimestampMixin, db.Model):
    __tablename__ = "tarifas_evento_detalle"

    id = db.Column(db.Integer, primary_key=True)
    tarifa_evento_id = db.Column(db.Integer, db.ForeignKey("tarifas_evento.id"), nullable=False, index=True)

    concepto = db.Column(db.String(120), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    tarifa = db.relationship(
        "TarifaEvento",
        backref=db.backref("detalles", lazy=True, cascade="all, delete-orphan")
    )


class EventoCategoriaHabilitada(TimestampMixin, db.Model):
    __tablename__ = "evento_categorias_habilitadas"

    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey("eventos.id"), nullable=False, index=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias_competencia.id"), nullable=False, index=True)

    evento = db.relationship("Evento", backref=db.backref("categorias_habilitadas", lazy=True, cascade="all, delete-orphan"))
    categoria = db.relationship("CategoriaCompetencia")


class EventoDivisionPoomsae(TimestampMixin, db.Model):
    __tablename__ = "evento_divisiones_poomsae"

    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey("eventos.id"), nullable=False, index=True)
    division_poomsae_id = db.Column(db.Integer, db.ForeignKey("divisiones_poomsae.id"), nullable=False, index=True)

    evento = db.relationship("Evento", backref=db.backref("divisiones_poomsae", lazy=True, cascade="all, delete-orphan"))
    division = db.relationship("DivisionPoomsae")