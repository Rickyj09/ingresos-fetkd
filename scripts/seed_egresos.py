from app import create_app
from app.extensions import db
from app.models.egresos import RubroEgreso


def main():
    app = create_app()

    with app.app_context():
        data = [
            ("LOGISTICA", "Logística"),
            ("PREMIACION", "Premiación"),
            ("ARBITRAJE", "Arbitraje"),
            ("ALIMENTACION", "Alimentación"),
            ("TRANSPORTE", "Transporte"),
            ("PUBLICIDAD", "Publicidad"),
            ("ADMIN", "Administrativo"),
            ("OTROS", "Otros"),
        ]

        creados = 0

        for codigo, nombre in data:
            existe = RubroEgreso.query.filter_by(codigo=codigo).first()
            if not existe:
                db.session.add(
                    RubroEgreso(
                        codigo=codigo,
                        nombre=nombre,
                        activo=True,
                    )
                )
                creados += 1

        db.session.commit()
        print(f"Rubros de egreso procesados. Nuevos creados: {creados}")


if __name__ == "__main__":
    main()