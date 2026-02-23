from decimal import Decimal
from sqlalchemy import func

from app.extensions import db
from app.models.pagos import Pago


def recalcular_inscripcion(ins) -> Decimal:
    """
    Recalcula pagado y saldo de una inscripción.

    Sprint actual:
    - ins.total ya viene definido (ingresado al crear la inscripción)
    - saldo = total - pagado
    """

    total = Decimal(str(ins.total or 0))

    pagado = (
        db.session.query(func.coalesce(func.sum(Pago.valor), 0))
        .filter(Pago.inscripcion_id == ins.id)
        .scalar()
    )
    pagado = Decimal(str(pagado or 0))

    ins.saldo = total - pagado

    return pagado