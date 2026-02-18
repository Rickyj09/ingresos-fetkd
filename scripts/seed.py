from app import create_app
from app.extensions import db
from app.models import Role, Rubro, User

def run_seed():
    app = create_app()
    with app.app_context():
        # Roles
        roles = ["ADMIN", "OPERADOR", "CONSULTA"]
        for r in roles:
            if not Role.query.filter_by(name=r).first():
                db.session.add(Role(name=r))

        # Rubros FEDETKD
        rubros = [
            ("CURSO", "Cursos"),
            ("AFILIACION", "Afiliaciones"),
            ("ASCENSO", "Ascensos"),
            ("GAL", "GAL"),
            ("COMPETENCIA", "Competencias"),
        ]
        for codigo, nombre in rubros:
            if not Rubro.query.filter_by(codigo=codigo).first():
                db.session.add(Rubro(codigo=codigo, nombre=nombre))

        db.session.commit()

        # Usuario admin (si no existe)
        admin_email = "admin@fetkd.local"
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            role_admin = Role.query.filter_by(name="ADMIN").first()
            admin = User(email=admin_email, role_id=role_admin.id, is_active=True)
            admin.set_password("Admin123*")  # cámbiala luego
            db.session.add(admin)
            db.session.commit()

        print("✅ Seed OK")
        print("Admin:", admin_email, "Pass: Admin123*")

if __name__ == "__main__":
    run_seed()