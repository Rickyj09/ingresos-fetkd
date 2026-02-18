from decimal import Decimal
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Evento, TarifaEvento, TarifaEventoDetalle, CategoriaCompetencia, DivisionPoomsae
from . import bp

TIPOS = ["FIJO", "POR_CATEGORIA", "POR_NIVEL_DAN", "POR_DIVISION_POOMSAE"]

@bp.route("/<int:evento_id>")
@login_required
def index(evento_id: int):
    evento = Evento.query.get_or_404(evento_id)
    tarifas = TarifaEvento.query.filter_by(evento_id=evento_id).order_by(TarifaEvento.prioridad.asc()).all()
    return render_template("tarifas/index.html", evento=evento, tarifas=tarifas, TIPOS=TIPOS)

@bp.route("/<int:evento_id>/nueva", methods=["GET", "POST"])
@login_required
def nueva(evento_id: int):
    evento = Evento.query.get_or_404(evento_id)

    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        vigencia_desde = request.form.get("vigencia_desde")
        vigencia_hasta = request.form.get("vigencia_hasta")
        tipo_calculo = request.form.get("tipo_calculo")
        valor = request.form.get("valor")
        prioridad = request.form.get("prioridad", type=int) or 1

        if tipo_calculo not in TIPOS:
            flash("Tipo de cálculo inválido", "danger")
            return render_template("tarifas/form.html", evento=evento, tarifa=None, TIPOS=TIPOS)

        t = TarifaEvento(
            evento_id=evento_id,
            nombre=nombre,
            vigencia_desde=vigencia_desde,
            vigencia_hasta=vigencia_hasta,
            tipo_calculo=tipo_calculo,
            valor=Decimal(valor) if valor and tipo_calculo == "FIJO" else None,
            prioridad=prioridad,
        )
        db.session.add(t)
        db.session.commit()
        flash("Tarifa creada", "success")
        return redirect(url_for("tarifas.index", evento_id=evento_id))

    return render_template("tarifas/form.html", evento=evento, tarifa=None, TIPOS=TIPOS)

@bp.route("/<int:evento_id>/<int:tarifa_id>/editar", methods=["GET", "POST"])
@login_required
def editar(evento_id: int, tarifa_id: int):
    evento = Evento.query.get_or_404(evento_id)
    tarifa = TarifaEvento.query.get_or_404(tarifa_id)

    if request.method == "POST":
        tarifa.nombre = (request.form.get("nombre") or "").strip()
        tarifa.vigencia_desde = request.form.get("vigencia_desde")
        tarifa.vigencia_hasta = request.form.get("vigencia_hasta")
        tarifa.tipo_calculo = request.form.get("tipo_calculo")
        tarifa.prioridad = request.form.get("prioridad", type=int) or 1
        valor = request.form.get("valor")

        tarifa.valor = Decimal(valor) if valor and tarifa.tipo_calculo == "FIJO" else None

        db.session.commit()
        flash("Tarifa actualizada", "success")
        return redirect(url_for("tarifas.index", evento_id=evento_id))

    return render_template("tarifas/form.html", evento=evento, tarifa=tarifa, TIPOS=TIPOS)

@bp.route("/<int:evento_id>/<int:tarifa_id>/eliminar", methods=["POST"])
@login_required
def eliminar(evento_id: int, tarifa_id: int):
    tarifa = TarifaEvento.query.get_or_404(tarifa_id)
    db.session.delete(tarifa)
    db.session.commit()
    flash("Tarifa eliminada", "success")
    return redirect(url_for("tarifas.index", evento_id=evento_id))

@bp.route("/<int:evento_id>/<int:tarifa_id>/detalles", methods=["GET", "POST"])
@login_required
def detalles(evento_id: int, tarifa_id: int):
    evento = Evento.query.get_or_404(evento_id)
    tarifa = TarifaEvento.query.get_or_404(tarifa_id)

    categorias = CategoriaCompetencia.query.order_by(CategoriaCompetencia.nombre.asc()).all()
    divisiones = DivisionPoomsae.query.order_by(DivisionPoomsae.nombre.asc()).all()

    if request.method == "POST":
        valor = request.form.get("valor")
        categoria_id = request.form.get("categoria_id", type=int)
        division_poomsae_id = request.form.get("division_poomsae_id", type=int)
        dan_nivel = request.form.get("dan_nivel", type=int)

        d = TarifaEventoDetalle(
            tarifa_id=tarifa_id,
            categoria_id=categoria_id if categoria_id else None,
            division_poomsae_id=division_poomsae_id if division_poomsae_id else None,
            dan_nivel=dan_nivel if dan_nivel else None,
            valor=Decimal(valor),
        )
        db.session.add(d)
        db.session.commit()
        flash("Detalle agregado", "success")
        return redirect(url_for("tarifas.detalles", evento_id=evento_id, tarifa_id=tarifa_id))

    detalles = TarifaEventoDetalle.query.filter_by(tarifa_id=tarifa_id).all()
    return render_template(
        "tarifas/detalles.html",
        evento=evento,
        tarifa=tarifa,
        detalles=detalles,
        categorias=categorias,
        divisiones=divisiones
    )

@bp.route("/<int:evento_id>/<int:tarifa_id>/detalles/<int:detalle_id>/eliminar", methods=["POST"])
@login_required
def eliminar_detalle(evento_id: int, tarifa_id: int, detalle_id: int):
    d = TarifaEventoDetalle.query.get_or_404(detalle_id)
    db.session.delete(d)
    db.session.commit()
    flash("Detalle eliminado", "success")
    return redirect(url_for("tarifas.detalles", evento_id=evento_id, tarifa_id=tarifa_id))