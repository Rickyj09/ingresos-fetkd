from decimal import Decimal, InvalidOperation

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models import Evento, TarifaEvento, TarifaEventoDetalle

from . import bp


@bp.route("/<int:evento_id>")
@login_required
def index(evento_id: int):
    evento = Evento.query.get_or_404(evento_id)
    tarifas = (
        TarifaEvento.query
        .filter_by(evento_id=evento_id)
        .order_by(TarifaEvento.nombre.asc(), TarifaEvento.id.asc())
        .all()
    )
    return render_template("tarifas/index.html", evento=evento, tarifas=tarifas)


@bp.route("/<int:evento_id>/nueva", methods=["GET", "POST"])
@login_required
def nueva(evento_id: int):
    evento = Evento.query.get_or_404(evento_id)

    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip()
        valor_raw = (request.form.get("valor") or "").strip()
        activo = True if request.form.get("activo") == "on" else False

        if not nombre:
            flash("El nombre es obligatorio.", "danger")
            return render_template("tarifas/form.html", evento=evento, tarifa=None)

        if not valor_raw:
            flash("El valor es obligatorio.", "danger")
            return render_template("tarifas/form.html", evento=evento, tarifa=None)

        valor_norm = valor_raw.replace(" ", "").replace("$", "").replace(",", ".")
        try:
            valor = Decimal(valor_norm)
            if valor < 0:
                raise ValueError()
        except (InvalidOperation, ValueError):
            flash("El valor ingresado no es válido.", "danger")
            return render_template("tarifas/form.html", evento=evento, tarifa=None)

        t = TarifaEvento(
            evento_id=evento_id,
            nombre=nombre,
            descripcion=descripcion or None,
            valor=valor,
            activo=activo,
        )
        db.session.add(t)
        db.session.commit()

        flash("Tarifa creada.", "success")
        return redirect(url_for("tarifas.index", evento_id=evento_id))

    return render_template("tarifas/form.html", evento=evento, tarifa=None)


@bp.route("/<int:evento_id>/<int:tarifa_id>/editar", methods=["GET", "POST"])
@login_required
def editar(evento_id: int, tarifa_id: int):
    evento = Evento.query.get_or_404(evento_id)
    tarifa = TarifaEvento.query.filter_by(id=tarifa_id, evento_id=evento_id).first_or_404()

    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip()
        valor_raw = (request.form.get("valor") or "").strip()
        activo = True if request.form.get("activo") == "on" else False

        if not nombre:
            flash("El nombre es obligatorio.", "danger")
            return render_template("tarifas/form.html", evento=evento, tarifa=tarifa)

        if not valor_raw:
            flash("El valor es obligatorio.", "danger")
            return render_template("tarifas/form.html", evento=evento, tarifa=tarifa)

        valor_norm = valor_raw.replace(" ", "").replace("$", "").replace(",", ".")
        try:
            valor = Decimal(valor_norm)
            if valor < 0:
                raise ValueError()
        except (InvalidOperation, ValueError):
            flash("El valor ingresado no es válido.", "danger")
            return render_template("tarifas/form.html", evento=evento, tarifa=tarifa)

        tarifa.nombre = nombre
        tarifa.descripcion = descripcion or None
        tarifa.valor = valor
        tarifa.activo = activo

        db.session.commit()
        flash("Tarifa actualizada.", "success")
        return redirect(url_for("tarifas.index", evento_id=evento_id))

    return render_template("tarifas/form.html", evento=evento, tarifa=tarifa)


@bp.route("/<int:evento_id>/<int:tarifa_id>/eliminar", methods=["POST"])
@login_required
def eliminar(evento_id: int, tarifa_id: int):
    tarifa = TarifaEvento.query.filter_by(id=tarifa_id, evento_id=evento_id).first_or_404()
    db.session.delete(tarifa)
    db.session.commit()

    flash("Tarifa eliminada.", "success")
    return redirect(url_for("tarifas.index", evento_id=evento_id))


@bp.route("/<int:evento_id>/<int:tarifa_id>/detalles", methods=["GET", "POST"])
@login_required
def detalles(evento_id: int, tarifa_id: int):
    evento = Evento.query.get_or_404(evento_id)
    tarifa = TarifaEvento.query.filter_by(id=tarifa_id, evento_id=evento_id).first_or_404()

    if request.method == "POST":
        concepto = (request.form.get("concepto") or "").strip()
        valor_raw = (request.form.get("valor") or "").strip()

        if not concepto or not valor_raw:
            flash("Concepto y valor son obligatorios.", "danger")
            return render_template(
                "tarifas/detalles.html",
                evento=evento,
                tarifa=tarifa,
                detalles=TarifaEventoDetalle.query.filter_by(tarifa_evento_id=tarifa_id).order_by(TarifaEventoDetalle.id.asc()).all(),
            )

        valor_norm = valor_raw.replace(" ", "").replace("$", "").replace(",", ".")
        try:
            valor = Decimal(valor_norm)
            if valor < 0:
                raise ValueError()
        except (InvalidOperation, ValueError):
            flash("Valor inválido.", "danger")
            return render_template(
                "tarifas/detalles.html",
                evento=evento,
                tarifa=tarifa,
                detalles=TarifaEventoDetalle.query.filter_by(tarifa_evento_id=tarifa_id).order_by(TarifaEventoDetalle.id.asc()).all(),
            )

        d = TarifaEventoDetalle(
            tarifa_evento_id=tarifa_id,
            concepto=concepto,
            valor=valor,
        )
        db.session.add(d)
        db.session.commit()

        flash("Detalle agregado.", "success")
        return redirect(url_for("tarifas.detalles", evento_id=evento_id, tarifa_id=tarifa_id))

    detalles = (
        TarifaEventoDetalle.query
        .filter_by(tarifa_evento_id=tarifa_id)
        .order_by(TarifaEventoDetalle.id.asc())
        .all()
    )

    return render_template(
        "tarifas/detalles.html",
        evento=evento,
        tarifa=tarifa,
        detalles=detalles,
    )


@bp.route("/<int:evento_id>/<int:tarifa_id>/detalles/<int:detalle_id>/eliminar", methods=["POST"])
@login_required
def eliminar_detalle(evento_id: int, tarifa_id: int, detalle_id: int):
    tarifa = TarifaEvento.query.filter_by(id=tarifa_id, evento_id=evento_id).first_or_404()
    d = TarifaEventoDetalle.query.filter_by(id=detalle_id, tarifa_evento_id=tarifa.id).first_or_404()

    db.session.delete(d)
    db.session.commit()

    flash("Detalle eliminado.", "success")
    return redirect(url_for("tarifas.detalles", evento_id=evento_id, tarifa_id=tarifa_id))