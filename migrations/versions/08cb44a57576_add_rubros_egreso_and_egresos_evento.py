"""add rubros_egreso and egresos_evento

Revision ID: 08cb44a57576
Revises: a1639b56b8fb
Create Date: 2026-03-13
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "08cb44a57576"
down_revision = "a1639b56b8fb"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rubros_egreso",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("codigo", sa.String(length=30), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo"),
    )
    op.create_index(op.f("ix_rubros_egreso_codigo"), "rubros_egreso", ["codigo"], unique=True)

    op.create_table(
        "egresos_evento",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column("rubro_egreso_id", sa.Integer(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=False),
        sa.Column("proveedor", sa.String(length=150), nullable=True),
        sa.Column("valor", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("numero_comprobante", sa.String(length=80), nullable=True),
        sa.Column("comprobante_path", sa.String(length=255), nullable=True),
        sa.Column("observacion", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["evento_id"], ["eventos.id"]),
        sa.ForeignKeyConstraint(["rubro_egreso_id"], ["rubros_egreso.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_egresos_evento_evento_id"), "egresos_evento", ["evento_id"], unique=False)
    op.create_index(op.f("ix_egresos_evento_rubro_egreso_id"), "egresos_evento", ["rubro_egreso_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_egresos_evento_rubro_egreso_id"), table_name="egresos_evento")
    op.drop_index(op.f("ix_egresos_evento_evento_id"), table_name="egresos_evento")
    op.drop_table("egresos_evento")

    op.drop_index(op.f("ix_rubros_egreso_codigo"), table_name="rubros_egreso")
    op.drop_table("rubros_egreso")