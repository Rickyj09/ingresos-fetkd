from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import ProductoServicio, Rubro
from . import bp

@bp.route("/")
@login_required
def index():
    rubro_id = request.args.get("rubro_id", type=int)
    q = (request.args.get("q") or "").strip()

    query = ProductoServicio.query.join(Rubro).order_by(ProductoServicio.nombre.asc())
    if rubro_id:
        query = query.filter(ProductoServicio.rubro_id == rubro_id)
    if q:
        query = query.filter(ProductoServicio.nombre.ilike(f"%{q}%"))

    productos = query.all()
    rubros = Rubro.query.order_by(Rubro.nombre.asc()).all()
    return render_template("productos/index.html", productos=productos, rubros=rubros, rubro_id=rubro_id, q=q)

@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    rubros = Rubro.query.order_by(Rubro.nombre.asc()).all()

    if request.method == "POST":
        rubro_id = request.form.get("rubro_id", type=int)
        nombre = (request.form.get("nombre") or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip() or None

        requiere_categoria = bool(request.form.get("requiere_categoria"))
        requiere_dan = bool(request.form.get("requiere_dan"))
        requiere_division_poomsae = bool(request.form.get("requiere_division_poomsae"))

        if not rubro_id or not nombre:
            flash("Rubro y Nombre son obligatorios", "danger")
            return render_template("productos/form.html", producto=None, rubros=rubros)

        p = ProductoServicio(
            rubro_id=rubro_id,
            nombre=nombre,
            descripcion=descripcion,
            requiere_categoria=requiere_categoria,
            requiere_dan=requiere_dan,
            requiere_division_poomsae=requiere_division_poomsae,
        )
        db.session.add(p)
        db.session.commit()
        flash("Producto/Servicio creado", "success")
        return redirect(url_for("productos.index"))

    return render_template("productos/form.html", producto=None, rubros=rubros)

@bp.route("/<int:producto_id>/editar", methods=["GET", "POST"])
@login_required
def editar(producto_id: int):
    producto = ProductoServicio.query.get_or_404(producto_id)
    rubros = Rubro.query.order_by(Rubro.nombre.asc()).all()

    if request.method == "POST":
        rubro_id = request.form.get("rubro_id", type=int)
        nombre = (request.form.get("nombre") or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip() or None

        producto.rubro_id = rubro_id
        producto.nombre = nombre
        producto.descripcion = descripcion
        producto.requiere_categoria = bool(request.form.get("requiere_categoria"))
        producto.requiere_dan = bool(request.form.get("requiere_dan"))
        producto.requiere_division_poomsae = bool(request.form.get("requiere_division_poomsae"))

        db.session.commit()
        flash("Producto/Servicio actualizado", "success")
        return redirect(url_for("productos.index"))

    return render_template("productos/form.html", producto=producto, rubros=rubros)

@bp.route("/<int:producto_id>/eliminar", methods=["POST"])
@login_required
def eliminar(producto_id: int):
    producto = ProductoServicio.query.get_or_404(producto_id)
    db.session.delete(producto)
    db.session.commit()
    flash("Producto/Servicio eliminado", "success")
    return redirect(url_for("productos.index"))