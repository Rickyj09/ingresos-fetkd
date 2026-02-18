from app.extensions import db
from .base import TimestampMixin

class Evento(TimestampMixin, db.Model):
    __tablename__ = "eventos"
    id = db.Column(db.Integer, primary_key=True)

    producto_id = db.Column(db.Integer, db.ForeignKey("productos_servicio.id"), nullable=False, index=True)
    producto = db.relationship("ProductoServicio", backref=db.backref("eventos", lazy=True))

    nombre = db.Column(db.String(190), nullable=False, index=True)
    anio = db.Column(db.Integer, nullable=False, index=True)

    sede = db.Column(db.String(190), nullable=True)
    fecha_inicio = db.Column(db.Date, nullable=True)
    fecha_fin = db.Column(db.Date, nullable=True)

    estado = db.Column(db.String(20), default="BORRADOR", nullable=False)  # BORRADOR/ABIERTO/CERRADO

class TarifaEvento(TimestampMixin, db.Model):
    __tablename__ = "tarifas_evento"
    id = db.Column(db.Integer, primary_key=True)

    evento_id = db.Column(db.Integer, db.ForeignKey("eventos.id"), nullable=False, index=True)
    evento = db.relationship("Evento", backref=db.backref("tarifas", lazy=True, cascade="all, delete-orphan"))

    nombre = db.Column(db.String(190), nullable=False)  # Early/Regular/Recargo...
    vigencia_desde = db.Column(db.Date, nullable=False)
    vigencia_hasta = db.Column(db.Date, nullable=False)

    # FIJO = usa valor
    # POR_CATEGORIA = usa TarifaEventoDetalle con categoria_id
    # POR_NIVEL_DAN = usa TarifaEventoDetalle con dan_nivel
    # POR_DIVISION_POOMSAE = usa TarifaEventoDetalle con division_poomsae_id
    tipo_calculo = db.Column(db.String(30), nullable=False)
    valor = db.Column(db.Numeric(10,2), nullable=True)

    prioridad = db.Column(db.Integer, default=1, nullable=False)

class TarifaEventoDetalle(db.Model):
    __tablename__ = "tarifas_evento_detalle"
    id = db.Column(db.Integer, primary_key=True)

    tarifa_id = db.Column(db.Integer, db.ForeignKey("tarifas_evento.id"), nullable=False, index=True)
    tarifa = db.relationship("TarifaEvento", backref=db.backref("detalles", lazy=True, cascade="all, delete-orphan"))

    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias_competencia.id"), nullable=True, index=True)
    division_poomsae_id = db.Column(db.Integer, db.ForeignKey("divisiones_poomsae.id"), nullable=True, index=True)
    dan_nivel = db.Column(db.Integer, nullable=True)

    valor = db.Column(db.Numeric(10,2), nullable=False)

class EventoCategoriaHabilitada(db.Model):
    __tablename__ = "evento_categorias_habilitadas"
    evento_id = db.Column(db.Integer, db.ForeignKey("eventos.id"), primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias_competencia.id"), primary_key=True)

class EventoDivisionPoomsae(db.Model):
    __tablename__ = "evento_divisiones_poomsae"
    evento_id = db.Column(db.Integer, db.ForeignKey("eventos.id"), primary_key=True)
    division_poomsae_id = db.Column(db.Integer, db.ForeignKey("divisiones_poomsae.id"), primary_key=True)