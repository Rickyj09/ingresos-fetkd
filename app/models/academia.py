from app.extensions import db
from app.models.base import TimestampMixin

class Academia(TimestampMixin, db.Model):
    __tablename__ = "academias"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(190), unique=True, nullable=False, index=True)

    ruc = db.Column(db.String(20), nullable=True)
    provincia = db.Column(db.String(100), nullable=True)
    ciudad = db.Column(db.String(100), nullable=True)
    direccion = db.Column(db.String(255), nullable=True)
    representante = db.Column(db.String(190), nullable=True)
    telefono = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(190), nullable=True)

    estado = db.Column(db.String(20), default="ACTIVA", nullable=False)  # ACTIVA/INACTIVA