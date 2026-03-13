from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models.egresos import EgresoEvento, RubroEgreso
from app.models.eventos import Evento

from . import bp


@bp.route("/")
@login_required
def index():
    evento_id = (request.args.get("evento_id") or "").strip()
    rubro_id = (request.args.get("rubro_id") or "").strip()

    q = (
        db.session.query(EgresoEvento, Evento, RubroEgreso)
        .join(Evento, Evento.id == EgresoEvento.evento_id)
        .join(RubroEgreso, RubroEgreso.id == EgresoEvento.rubro_egreso_id)
        .order_by(EgresoEvento.fecha.desc(), EgresoEvento.id.desc())
    )

    if evento_id.isdigit():
        q = q.filter(EgresoEvento.evento_id == int(evento_id))

    if rubro_id.isdigit():
        q = q.filter(EgresoEvento.rubro_egreso_id == int(rubro_id))

    rows = q.all()

    eventos = Evento.query.order_by(Evento.anio.desc(), Evento.nombre.asc()).all()
    rubros = RubroEgreso.query.order_by(RubroEgreso.nombre.asc()).all()

    filtros = {
        "evento_id": evento_id,
        "rubro_id": rubro_id,
    }

    return render_template(
        "egresos/index.html",
        rows=rows,
        eventos=eventos,
        rubros=rubros,
        filtros=filtros,
    )


@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    eventos = Evento.query.order_by(Evento.anio.desc(), Evento.nombre.asc()).all()
    rubros = RubroEgreso.query.order_by(RubroEgreso.nombre.asc()).all()

    if request.method == "POST":
        evento_id = (request.form.get("evento_id") or "").strip()
        rubro_egreso_id = (request.form.get("rubro_egreso_id") or "").strip()
        fecha_str = (request.form.get("fecha") or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip()
        proveedor = (request.form.get("proveedor") or "").strip()
        valor_raw = (request.form.get("valor") or "").strip()
        numero_comprobante = (request.form.get("numero_comprobante") or "").strip()
        observacion = (request.form.get("observacion") or "").strip()

        if not evento_id.isdigit() or not rubro_egreso_id.isdigit() or not fecha_str or not descripcion or not valor_raw:
            flash("Evento, rubro, fecha, descripción y valor son obligatorios.", "danger")
            return render_template("egresos/form.html", item=None, eventos=eventos, rubros=rubros)

        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Fecha inválida. Use formato YYYY-MM-DD.", "danger")
            return render_template("egresos/form.html", item=None, eventos=eventos, rubros=rubros)

        valor_norm = valor_raw.replace(" ", "").replace("$", "").replace(",", ".")
        try:
            valor = Decimal(valor_norm)
            if valor < 0:
                raise ValueError()
        except (InvalidOperation, ValueError):
            flash("Valor inválido.", "danger")
            return render_template("egresos/form.html", item=None, eventos=eventos, rubros=rubros)

        item = EgresoEvento(
            evento_id=int(evento_id),
            rubro_egreso_id=int(rubro_egreso_id),
            fecha=fecha,
            descripcion=descripcion,
            proveedor=proveedor or None,
            valor=valor,
            numero_comprobante=numero_comprobante or None,
            observacion=observacion or None,
        )
        db.session.add(item)
        db.session.commit()

        flash("Egreso registrado correctamente.", "success")
        return redirect(url_for("egresos.index"))

    return render_template("egresos/form.html", item=None, eventos=eventos, rubros=rubros)


@bp.route("/<int:item_id>/editar", methods=["GET", "POST"])
@login_required
def editar(item_id):
    item = EgresoEvento.query.get_or_404(item_id)
    eventos = Evento.query.order_by(Evento.anio.desc(), Evento.nombre.asc()).all()
    rubros = RubroEgreso.query.order_by(RubroEgreso.nombre.asc()).all()

    if request.method == "POST":
        evento_id = (request.form.get("evento_id") or "").strip()
        rubro_egreso_id = (request.form.get("rubro_egreso_id") or "").strip()
        fecha_str = (request.form.get("fecha") or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip()
        proveedor = (request.form.get("proveedor") or "").strip()
        valor_raw = (request.form.get("valor") or "").strip()
        numero_comprobante = (request.form.get("numero_comprobante") or "").strip()
        observacion = (request.form.get("observacion") or "").strip()

        if not evento_id.isdigit() or not rubro_egreso_id.isdigit() or not fecha_str or not descripcion or not valor_raw:
            flash("Evento, rubro, fecha, descripción y valor son obligatorios.", "danger")
            return render_template("egresos/form.html", item=item, eventos=eventos, rubros=rubros)

        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Fecha inválida. Use formato YYYY-MM-DD.", "danger")
            return render_template("egresos/form.html", item=item, eventos=eventos, rubros=rubros)

        valor_norm = valor_raw.replace(" ", "").replace("$", "").replace(",", ".")
        try:
            valor = Decimal(valor_norm)
            if valor < 0:
                raise ValueError()
        except (InvalidOperation, ValueError):
            flash("Valor inválido.", "danger")
            return render_template("egresos/form.html", item=item, eventos=eventos, rubros=rubros)

        item.evento_id = int(evento_id)
        item.rubro_egreso_id = int(rubro_egreso_id)
        item.fecha = fecha
        item.descripcion = descripcion
        item.proveedor = proveedor or None
        item.valor = valor
        item.numero_comprobante = numero_comprobante or None
        item.observacion = observacion or None

        db.session.commit()
        flash("Egreso actualizado correctamente.", "success")
        return redirect(url_for("egresos.index"))

    return render_template("egresos/form.html", item=item, eventos=eventos, rubros=rubros)


@bp.route("/<int:item_id>/eliminar", methods=["POST"])
@login_required
def eliminar(item_id):
    item = EgresoEvento.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()

    flash("Egreso eliminado.", "warning")
    return redirect(url_for("egresos.index"))