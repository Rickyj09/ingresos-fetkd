from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Academia
from . import bp

@bp.route("/")
@login_required
def index():
    academias = Academia.query.order_by(Academia.nombre.asc()).all()
    return render_template("academias/index.html", academias=academias)

@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        if not nombre:
            flash("Nombre es obligatorio", "danger")
            return render_template("academias/form.html", academia=None)

        if Academia.query.filter_by(nombre=nombre).first():
            flash("Ya existe una academia con ese nombre", "warning")
            return render_template("academias/form.html", academia=None)

        a = Academia(
            nombre=nombre,
            ruc=(request.form.get("ruc") or "").strip() or None,
            provincia=(request.form.get("provincia") or "").strip() or None,
            ciudad=(request.form.get("ciudad") or "").strip() or None,
            direccion=(request.form.get("direccion") or "").strip() or None,
            representante=(request.form.get("representante") or "").strip() or None,
            telefono=(request.form.get("telefono") or "").strip() or None,
            email=(request.form.get("email") or "").strip() or None,
            estado=request.form.get("estado") or "ACTIVA",
        )
        db.session.add(a)
        db.session.commit()
        flash("Academia creada", "success")
        return redirect(url_for("academias.index"))

    return render_template("academias/form.html", academia=None)

@bp.route("/<int:academia_id>/editar", methods=["GET", "POST"])
@login_required
def editar(academia_id: int):
    academia = Academia.query.get_or_404(academia_id)

    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        if not nombre:
            flash("Nombre es obligatorio", "danger")
            return render_template("academias/form.html", academia=academia)

        existe = Academia.query.filter(Academia.nombre == nombre, Academia.id != academia.id).first()
        if existe:
            flash("Ya existe otra academia con ese nombre", "warning")
            return render_template("academias/form.html", academia=academia)

        academia.nombre = nombre
        academia.ruc = (request.form.get("ruc") or "").strip() or None
        academia.provincia = (request.form.get("provincia") or "").strip() or None
        academia.ciudad = (request.form.get("ciudad") or "").strip() or None
        academia.direccion = (request.form.get("direccion") or "").strip() or None
        academia.representante = (request.form.get("representante") or "").strip() or None
        academia.telefono = (request.form.get("telefono") or "").strip() or None
        academia.email = (request.form.get("email") or "").strip() or None
        academia.estado = request.form.get("estado") or "ACTIVA"

        db.session.commit()
        flash("Academia actualizada", "success")
        return redirect(url_for("academias.index"))

    return render_template("academias/form.html", academia=academia)

@bp.route("/<int:academia_id>/eliminar", methods=["POST"])
@login_required
def eliminar(academia_id: int):
    academia = Academia.query.get_or_404(academia_id)
    db.session.delete(academia)
    db.session.commit()
    flash("Academia eliminada", "success")
    return redirect(url_for("academias.index"))