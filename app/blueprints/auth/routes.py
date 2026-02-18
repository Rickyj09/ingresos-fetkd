from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import User
from . import bp

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = User.query.filter_by(email=email, is_active=True).first()
        if not user or not user.check_password(password):
            flash("Credenciales inválidas", "danger")
            return render_template("auth/login.html")

        login_user(user)
        return redirect(url_for("academias.index"))

    return render_template("auth/login.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))