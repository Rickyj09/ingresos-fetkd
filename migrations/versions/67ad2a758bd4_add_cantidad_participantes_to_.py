"""add cantidad_participantes to inscripciones

Revision ID: 67ad2a758bd4
Revises: 4496d06107f6
Create Date: 2026-02-23
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "67ad2a758bd4"
down_revision = "4496d06107f6"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("inscripciones", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "cantidad_participantes",
                sa.Integer(),
                nullable=False,
                server_default="1",
            )
        )


def downgrade():
    with op.batch_alter_table("inscripciones", schema=None) as batch_op:
        batch_op.drop_column("cantidad_participantes")