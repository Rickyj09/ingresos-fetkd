from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Evento, ProductoServicio
from . import bp

@bp.route("/")
@login_required
def index():
    anio = request.args.get("anio", type=int)
    producto_id = request.args.get("producto_id", type=int)

    query = Evento.query.join(ProductoServicio).order_by(Evento.anio.desc(), Evento.nombre.asc())
    if anio:
        query = query.filter(Evento.anio == anio)
    if producto_id:
        query = query.filter(Evento.producto_id == producto_id)

    eventos = query.all()
    productos = ProductoServicio.query.order_by(ProductoServicio.nombre.asc()).all()
    return render_template("eventos/index.html", eventos=eventos, productos=productos, anio=anio, producto_id=producto_id)

@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    productos = ProductoServicio.query.order_by(ProductoServicio.nombre.asc()).all()

    if request.method == "POST":
        producto_id = request.form.get("producto_id", type=int)
        nombre = (request.form.get("nombre") or "").strip()
        anio = request.form.get("anio", type=int)
        sede = (request.form.get("sede") or "").strip() or None
        fecha_inicio = request.form.get("fecha_inicio") or None
        fecha_fin = request.form.get("fecha_fin") or None
        estado = request.form.get("estado") or "BORRADOR"

        if not producto_id or not nombre or not anio:
            flash("Producto, Nombre y Año son obligatorios", "danger")
            return render_template("eventos/form.html", evento=None, productos=productos)

        e = Evento(
            producto_id=producto_id,
            nombre=nombre,
            anio=anio,
            sede=sede,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado=estado,
        )
        db.session.add(e)
        db.session.commit()
        flash("Evento creado", "success")
        return redirect(url_for("eventos.index"))

    return render_template("eventos/form.html", evento=None, productos=productos)

@bp.route("/<int:evento_id>/editar", methods=["GET", "POST"])
@login_required
def editar(evento_id: int):
    evento = Evento.query.get_or_404(evento_id)
    productos = ProductoServicio.query.order_by(ProductoServicio.nombre.asc()).all()

    if request.method == "POST":
        evento.producto_id = request.form.get("producto_id", type=int)
        evento.nombre = (request.form.get("nombre") or "").strip()
        evento.anio = request.form.get("anio", type=int)
        evento.sede = (request.form.get("sede") or "").strip() or None
        evento.fecha_inicio = request.form.get("fecha_inicio") or None
        evento.fecha_fin = request.form.get("fecha_fin") or None
        evento.estado = request.form.get("estado") or "BORRADOR"

        db.session.commit()
        flash("Evento actualizado", "success")
        return redirect(url_for("eventos.index"))

    return render_template("eventos/form.html", evento=evento, productos=productos)

@bp.route("/<int:evento_id>/eliminar", methods=["POST"])
@login_required
def eliminar(evento_id: int):
    evento = Evento.query.get_or_404(evento_id)
    db.session.delete(evento)
    db.session.commit()
    flash("Evento eliminado", "success")
    return redirect(url_for("eventos.index"))