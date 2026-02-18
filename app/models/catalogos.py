from app.extensions import db
from .base import TimestampMixin

class Rubro(db.Model):
    __tablename__ = "rubros"
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False)  # CURSO/AFILIACION/ASCENSO/GAL/COMPETENCIA
    nombre = db.Column(db.String(100), nullable=False)

class ProductoServicio(TimestampMixin, db.Model):
    __tablename__ = "productos_servicio"
    id = db.Column(db.Integer, primary_key=True)

    rubro_id = db.Column(db.Integer, db.ForeignKey("rubros.id"), nullable=False, index=True)
    rubro = db.relationship("Rubro", backref=db.backref("productos", lazy=True))

    nombre = db.Column(db.String(190), nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=True)

    # “reglas” para UI/validación (NO obliga a usarlo, pero guía el evento/inscripción)
    requiere_categoria = db.Column(db.Boolean, default=False, nullable=False)
    requiere_dan = db.Column(db.Boolean, default=False, nullable=False)
    requiere_division_poomsae = db.Column(db.Boolean, default=False, nullable=False)

class CategoriaCompetencia(TimestampMixin, db.Model):
    __tablename__ = "categorias_competencia"
    id = db.Column(db.Integer, primary_key=True)

    modalidad = db.Column(db.String(20), nullable=False)  # COMBATE/POOMSAE/PARA_TKD
    sexo = db.Column(db.String(10), nullable=True)        # M/F/MIXTO o None
    edad_min = db.Column(db.Integer, nullable=True)
    edad_max = db.Column(db.Integer, nullable=True)
    peso_min = db.Column(db.Numeric(6,2), nullable=True)
    peso_max = db.Column(db.Numeric(6,2), nullable=True)

    nombre = db.Column(db.String(190), nullable=False, index=True)

class DivisionPoomsae(TimestampMixin, db.Model):
    __tablename__ = "divisiones_poomsae"
    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(190), nullable=False, unique=True)
    nivel = db.Column(db.String(30), nullable=True)  # Novatos/Intermedios/Avanzados (si aplica)
    edad_min = db.Column(db.Integer, nullable=True)
    edad_max = db.Column(db.Integer, nullable=True)