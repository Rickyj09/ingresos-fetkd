from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models.inscripciones import Inscripcion, InscripcionDetalle
from app.models.academia import Academia
from app.models.eventos import Evento, TarifaEvento
from app.models.catalogos import ProductoServicio
from app.models.pagos import Pago
from app.utils.inscripcion_calc import recalcular_inscripcion

from . import bp


@bp.route("/")
@login_required
def index():
    anio = (request.args.get("anio") or "").strip()
    evento_id = (request.args.get("evento_id") or "").strip()
    academia_id = (request.args.get("academia_id") or "").strip()
    estado = (request.args.get("estado") or "").strip()

    q = (
        db.session.query(Inscripcion, Evento, Academia, ProductoServicio)
        .join(Evento, Evento.id == Inscripcion.evento_id)
        .join(ProductoServicio, ProductoServicio.id == Evento.producto_id)
        .join(Academia, Academia.id == Inscripcion.academia_id)
        .order_by(Inscripcion.id.desc())
    )

    if anio.isdigit():
        q = q.filter(Evento.anio == int(anio))
    if evento_id.isdigit():
        q = q.filter(Inscripcion.evento_id == int(evento_id))
    if academia_id.isdigit():
        q = q.filter(Inscripcion.academia_id == int(academia_id))
    if estado:
        q = q.filter(Inscripcion.estado == estado)

    rows = q.all()

    eventos = Evento.query.order_by(Evento.anio.desc(), Evento.nombre.asc()).all()
    academias = Academia.query.order_by(Academia.nombre.asc()).all()

    filtros = {
        "anio": anio,
        "evento_id": evento_id,
        "academia_id": academia_id,
        "estado": estado,
    }

    return render_template(
        "inscripciones/index.html",
        rows=rows,
        eventos=eventos,
        academias=academias,
        filtros=filtros,
        estados=["BORRADOR", "ENVIADA", "CONFIRMADA"],
    )


@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    eventos = Evento.query.order_by(Evento.anio.desc(), Evento.nombre.asc()).all()
    academias = Academia.query.order_by(Academia.nombre.asc()).all()

    if not eventos:
        flash("No existen eventos registrados.", "warning")
        return render_template(
            "inscripciones/nuevo.html",
            eventos=[],
            academias=academias,
            tarifas=[],
            evento_seleccionado_id=None,
        )

    evento_seleccionado_id = request.values.get("evento_id", type=int)
    if not evento_seleccionado_id:
        evento_seleccionado_id = eventos[0].id

    evento = Evento.query.get_or_404(evento_seleccionado_id)

    tarifas = (
        TarifaEvento.query
        .filter_by(evento_id=evento.id, activo=True)
        .order_by(TarifaEvento.nombre.asc(), TarifaEvento.id.asc())
        .all()
    )

    if request.method == "POST":
        academia_id = request.form.get("academia_id", type=int)

        if not academia_id:
            flash("Debes seleccionar una academia.", "danger")
            return render_template(
                "inscripciones/nuevo.html",
                eventos=eventos,
                academias=academias,
                tarifas=tarifas,
                evento_seleccionado_id=evento.id,
            )

        academia = Academia.query.get_or_404(academia_id)

        existente = Inscripcion.query.filter_by(
            evento_id=evento.id,
            academia_id=academia.id
        ).first()

        if existente:
            flash("Ya existe una inscripción para esta academia en el evento seleccionado.", "warning")
            return render_template(
                "inscripciones/nuevo.html",
                eventos=eventos,
                academias=academias,
                tarifas=tarifas,
                evento_seleccionado_id=evento.id,
            )

        total_participantes = 0
        subtotal_general = Decimal("0.00")
        detalles_crear = []

        for tarifa in tarifas:
            cantidad = request.form.get(f"cantidad_{tarifa.id}", type=int) or 0

            if cantidad < 0:
                cantidad = 0

            if cantidad == 0:
                continue

            valor_unitario = Decimal(str(tarifa.valor or 0))
            total_linea = valor_unitario * cantidad

            total_participantes += cantidad
            subtotal_general += total_linea

            detalles_crear.append({
                "tarifa_evento_id": tarifa.id,
                "concepto": tarifa.nombre,
                "cantidad": cantidad,
                "valor_unitario": valor_unitario,
                "total": total_linea,
            })

        if total_participantes <= 0:
            flash("Debes ingresar al menos una cantidad en alguna tarifa.", "danger")
            return render_template(
                "inscripciones/nuevo.html",
                eventos=eventos,
                academias=academias,
                tarifas=tarifas,
                evento_seleccionado_id=evento.id,
            )

        inscripcion = Inscripcion(
            evento_id=evento.id,
            academia_id=academia.id,
            estado="BORRADOR",
            cantidad_participantes=total_participantes,
            subtotal=subtotal_general,
            descuentos=Decimal("0.00"),
            total=subtotal_general,
            saldo=subtotal_general,
        )

        db.session.add(inscripcion)
        db.session.flush()

        for d in detalles_crear:
            detalle = InscripcionDetalle(
                inscripcion_id=inscripcion.id,
                tarifa_evento_id=d["tarifa_evento_id"],
                concepto=d["concepto"],
                cantidad=d["cantidad"],
                valor_unitario=d["valor_unitario"],
                total=d["total"],
            )
            db.session.add(detalle)

        db.session.commit()

        flash("Inscripción creada correctamente.", "success")
        return redirect(url_for("inscripciones.index"))

    return render_template(
        "inscripciones/nuevo.html",
        eventos=eventos,
        academias=academias,
        tarifas=tarifas,
        evento_seleccionado_id=evento.id,
    )


@bp.route("/<int:inscripcion_id>/pagos")
@login_required
def pagos(inscripcion_id):
    ins = Inscripcion.query.get_or_404(inscripcion_id)

    pagos_list = (
        Pago.query
        .filter_by(inscripcion_id=inscripcion_id)
        .order_by(Pago.fecha_pago.desc(), Pago.id.desc())
        .all()
    )

    pagado = recalcular_inscripcion(ins)
    db.session.commit()

    return render_template(
        "inscripciones/pagos.html",
        ins=ins,
        pagos=pagos_list,
        pagado=float(pagado or 0),
    )


@bp.route("/<int:inscripcion_id>/pagos/nuevo", methods=["POST"])
@login_required
def pagos_nuevo(inscripcion_id):
    ins = Inscripcion.query.get_or_404(inscripcion_id)

    fecha_pago = (request.form.get("fecha_pago") or "").strip()
    valor_raw = (request.form.get("valor") or "").strip()
    metodo = (request.form.get("metodo") or "").strip()
    referencia = (request.form.get("referencia") or "").strip()
    observacion = (request.form.get("observacion") or "").strip()

    if not fecha_pago or not valor_raw:
        flash("Fecha y valor son obligatorios.", "danger")
        return redirect(url_for("inscripciones.pagos", inscripcion_id=ins.id))

    try:
        fecha_dt = datetime.strptime(fecha_pago, "%Y-%m-%d").date()
    except ValueError:
        flash("Formato de fecha inválido. Use YYYY-MM-DD.", "danger")
        return redirect(url_for("inscripciones.pagos", inscripcion_id=ins.id))

    valor_norm = valor_raw.replace(" ", "").replace("$", "").replace(",", ".")
    try:
        valor_dec = Decimal(valor_norm)
        if valor_dec <= 0:
            raise ValueError()
    except (InvalidOperation, ValueError):
        flash("Valor inválido. Debe ser un número mayor a 0.", "danger")
        return redirect(url_for("inscripciones.pagos", inscripcion_id=ins.id))

    p = Pago(
        inscripcion_id=ins.id,
        fecha_pago=fecha_dt,
        valor=valor_dec,
        metodo=metodo or None,
        referencia=referencia or None,
        observacion=observacion or None,
    )
    db.session.add(p)

    recalcular_inscripcion(ins)
    db.session.commit()

    flash("Pago registrado.", "success")
    return redirect(url_for("inscripciones.pagos", inscripcion_id=ins.id))


@bp.route("/<int:inscripcion_id>/pagos/<int:pago_id>/eliminar", methods=["POST"])
@login_required
def pagos_eliminar(inscripcion_id, pago_id):
    ins = Inscripcion.query.get_or_404(inscripcion_id)
    p = Pago.query.filter_by(id=pago_id, inscripcion_id=inscripcion_id).first_or_404()

    db.session.delete(p)
    recalcular_inscripcion(ins)
    db.session.commit()

    flash("Pago eliminado.", "warning")
    return redirect(url_for("inscripciones.pagos", inscripcion_id=ins.id))