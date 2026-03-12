from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models.inscripciones import Inscripcion
from app.models.academia import Academia
from app.models.eventos import Evento
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

    if request.method == "POST":
        evento_id_str = (request.form.get("evento_id") or "").strip()
        academia_id_str = (request.form.get("academia_id") or "").strip()
        cantidad_str = (request.form.get("cantidad_participantes") or "1").strip()

        if not evento_id_str.isdigit() or not academia_id_str.isdigit():
            flash("Debe seleccionar Evento y Academia.", "danger")
            return render_template("inscripciones/nuevo.html", eventos=eventos, academias=academias)

        if not cantidad_str.isdigit() or int(cantidad_str) <= 0:
            flash("La cantidad de participantes debe ser un número mayor a 0.", "danger")
            return render_template("inscripciones/nuevo.html", eventos=eventos, academias=academias)

        evento_id = int(evento_id_str)
        academia_id = int(academia_id_str)
        cantidad_participantes = int(cantidad_str)

        evento = Evento.query.get(evento_id)
        if not evento:
            flash("Evento no encontrado.", "danger")
            return render_template("inscripciones/nuevo.html", eventos=eventos, academias=academias)

        existe = (
            Inscripcion.query
            .filter(
                Inscripcion.evento_id == evento_id,
                Inscripcion.academia_id == academia_id
            )
            .first()
        )
        if existe:
            flash("Ya existe una inscripción para esa academia en ese evento.", "warning")
            return render_template("inscripciones/nuevo.html", eventos=eventos, academias=academias)

        valor_base = Decimal(str(evento.valor_base or 0))
        subtotal = Decimal(cantidad_participantes) * valor_base
        descuentos = Decimal("0.00")
        total = subtotal - descuentos
        saldo = total

        ins = Inscripcion(
            evento_id=evento_id,
            academia_id=academia_id,
            estado="BORRADOR",
            cantidad_participantes=cantidad_participantes,
            subtotal=subtotal,
            descuentos=descuentos,
            total=total,
            saldo=saldo,
        )

        db.session.add(ins)
        db.session.commit()

        flash("Inscripción creada correctamente.", "success")
        return redirect(url_for("inscripciones.index"))

    return render_template("inscripciones/nuevo.html", eventos=eventos, academias=academias)


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