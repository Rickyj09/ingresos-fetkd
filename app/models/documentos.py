from app.extensions import db
from .base import TimestampMixin

class Numerador(db.Model):
    __tablename__ = "numeradores"
    id = db.Column(db.Integer, primary_key=True)

    tipo_doc = db.Column(db.String(20), nullable=False)  # RECIBO/FACTURA
    serie = db.Column(db.String(20), nullable=False)
    ultimo_numero = db.Column(db.Integer, default=0, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("tipo_doc", "serie", name="uq_numerador_tipo_serie"),
    )

class DocumentoCobro(TimestampMixin, db.Model):
    __tablename__ = "documentos_cobro"
    id = db.Column(db.Integer, primary_key=True)

    inscripcion_id = db.Column(db.Integer, db.ForeignKey("inscripciones.id"), nullable=False, index=True)
    inscripcion = db.relationship("Inscripcion", backref=db.backref("documentos", lazy=True, cascade="all, delete-orphan"))

    tipo = db.Column(db.String(20), nullable=False)  # RECIBO/FACTURA
    serie = db.Column(db.String(20), nullable=False)
    numero = db.Column(db.Integer, nullable=False)

    fecha_emision = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), default="EMITIDO", nullable=False)  # EMITIDO/ANULADO

    total = db.Column(db.Numeric(12,2), nullable=False)
    saldo_al_emitir = db.Column(db.Numeric(12,2), nullable=False)

    pdf_path = db.Column(db.String(255), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("tipo", "serie", "numero", name="uq_documento_numero"),
    )