from flask import render_template, request
from flask_login import login_required
from sqlalchemy import func, distinct

from app.extensions import db
from app.models import (
    Pago, Inscripcion, InscripcionDetalle,
    Academia, Evento, ProductoServicio, Rubro
)
from . import bp


def _get_filters():
    return {
        "desde": request.args.get("desde"),          # YYYY-MM-DD
        "hasta": request.args.get("hasta"),          # YYYY-MM-DD
        "anio": request.args.get("anio", type=int),
        "academia_id": request.args.get("academia_id", type=int),
        "evento_id": request.args.get("evento_id", type=int),
    }


def _apply_filters(query, f):
    if f["desde"]:
        query = query.filter(Pago.fecha_pago >= f["desde"])
    if f["hasta"]:
        query = query.filter(Pago.fecha_pago <= f["hasta"])
    if f["anio"]:
        query = query.filter(Evento.anio == f["anio"])
    if f["academia_id"]:
        query = query.filter(Academia.id == f["academia_id"])
    if f["evento_id"]:
        query = query.filter(Evento.id == f["evento_id"])
    return query


@bp.route("/")
@login_required
def index():
    return render_template("reportes/index.html")


# 1) Ingreso que generó cada club (Academia)
@bp.route("/clubes")
@login_required
def clubes():
    f = _get_filters()

    q = (
        db.session.query(
            Academia.id,
            Academia.nombre,
            func.coalesce(func.sum(Pago.valor), 0).label("total"),
            func.count(Pago.id).label("pagos"),
            func.count(distinct(Inscripcion.id)).label("inscripciones"),
        )
        .join(Inscripcion, Inscripcion.academia_id == Academia.id)
        .join(Pago, Pago.inscripcion_id == Inscripcion.id)
        .join(Evento, Evento.id == Inscripcion.evento_id)
        .join(ProductoServicio, ProductoServicio.id == Evento.producto_id)
        .join(Rubro, Rubro.id == ProductoServicio.rubro_id)
        .group_by(Academia.id, Academia.nombre)
        .order_by(func.sum(Pago.valor).desc())
    )

    q = _apply_filters(q, f)
    rows = q.all()
    return render_template("reportes/clubes.html", rows=rows, filtros=f)


# 2) Ingreso por evento o competencia (filtro opcional rubro=COMPETENCIA)
@bp.route("/eventos")
@login_required
def eventos():
    f = _get_filters()
    rubro = (request.args.get("rubro") or "").strip().upper()  # ej: COMPETENCIA

    q = (
        db.session.query(
            Evento.id,
            Evento.anio,
            Rubro.codigo.label("rubro"),
            ProductoServicio.nombre.label("producto"),
            Evento.nombre.label("evento"),
            func.coalesce(func.sum(Pago.valor), 0).label("total"),
            func.count(distinct(Inscripcion.academia_id)).label("academias"),
            func.count(Pago.id).label("pagos"),
        )
        .join(Inscripcion, Inscripcion.evento_id == Evento.id)
        .join(Pago, Pago.inscripcion_id == Inscripcion.id)
        .join(ProductoServicio, ProductoServicio.id == Evento.producto_id)
        .join(Rubro, Rubro.id == ProductoServicio.rubro_id)
        .group_by(Evento.id, Evento.anio, Rubro.codigo, ProductoServicio.nombre, Evento.nombre)
        .order_by(func.sum(Pago.valor).desc())
    )

    q = _apply_filters(q, f)
    if rubro:
        q = q.filter(Rubro.codigo == rubro)

    rows = q.all()
    return render_template("reportes/eventos.html", rows=rows, filtros=f, rubro=rubro)


# 3) Afiliaciones: Nueva vs Renovación (por ProductoServicio) usando rubro AFILIACION
@bp.route("/afiliaciones")
@login_required
def afiliaciones():
    f = _get_filters()

    q = (
        db.session.query(
            ProductoServicio.id,
            ProductoServicio.nombre.label("tipo"),
            func.coalesce(func.sum(Pago.valor), 0).label("total"),
            func.count(distinct(Inscripcion.id)).label("inscripciones"),
            func.count(distinct(Inscripcion.academia_id)).label("academias"),
        )
        .join(Evento, Evento.producto_id == ProductoServicio.id)
        .join(Inscripcion, Inscripcion.evento_id == Evento.id)
        .join(Pago, Pago.inscripcion_id == Inscripcion.id)
        .join(Rubro, Rubro.id == ProductoServicio.rubro_id)
        .filter(Rubro.codigo == "AFILIACION")
        .group_by(ProductoServicio.id, ProductoServicio.nombre)
        .order_by(func.sum(Pago.valor).desc())
    )

    q = _apply_filters(q, f)
    rows = q.all()
    return render_template("reportes/afiliaciones.html", rows=rows, filtros=f)


# 4) Ascensos por Dan 1..9 y por Nacional/Internacional
# Distinguimos Nacional/Internacional por el ProductoServicio.nombre (Ascenso Dan Nacional / Internacional)
@bp.route("/ascensos")
@login_required
def ascensos():
    f = _get_filters()

    q = (
        db.session.query(
            ProductoServicio.nombre.label("tipo_ascenso"),
            InscripcionDetalle.dan_nivel.label("dan"),
            func.coalesce(func.sum(Pago.valor), 0).label("total"),
            func.count(distinct(Inscripcion.id)).label("inscripciones"),
            func.count(distinct(Inscripcion.academia_id)).label("academias"),
        )
        .join(Inscripcion, Inscripcion.id == InscripcionDetalle.inscripcion_id)
        .join(Pago, Pago.inscripcion_id == Inscripcion.id)
        .join(Evento, Evento.id == Inscripcion.evento_id)
        .join(ProductoServicio, ProductoServicio.id == Evento.producto_id)
        .join(Rubro, Rubro.id == ProductoServicio.rubro_id)
        .filter(Rubro.codigo == "ASCENSO")
        .filter(InscripcionDetalle.dan_nivel.isnot(None))
        .group_by(ProductoServicio.nombre, InscripcionDetalle.dan_nivel)
        .order_by(ProductoServicio.nombre.asc(), InscripcionDetalle.dan_nivel.asc())
    )

    q = _apply_filters(q, f)
    rows = q.all()
    return render_template("reportes/ascensos.html", rows=rows, filtros=f)


# 5) GAL por academia (Nacional/Internacional por ProductoServicio.nombre)
@bp.route("/gal")
@login_required
def gal():
    f = _get_filters()

    q = (
        db.session.query(
            Academia.id,
            Academia.nombre,
            ProductoServicio.nombre.label("tipo_gal"),
            func.coalesce(func.sum(Pago.valor), 0).label("total"),
            func.count(Pago.id).label("pagos"),
        )
        .join(Inscripcion, Inscripcion.academia_id == Academia.id)
        .join(Pago, Pago.inscripcion_id == Inscripcion.id)
        .join(Evento, Evento.id == Inscripcion.evento_id)
        .join(ProductoServicio, ProductoServicio.id == Evento.producto_id)
        .join(Rubro, Rubro.id == ProductoServicio.rubro_id)
        .filter(Rubro.codigo == "GAL")
        .group_by(Academia.id, Academia.nombre, ProductoServicio.nombre)
        .order_by(func.sum(Pago.valor).desc())
    )

    q = _apply_filters(q, f)
    rows = q.all()
    return render_template("reportes/gal.html", rows=rows, filtros=f)