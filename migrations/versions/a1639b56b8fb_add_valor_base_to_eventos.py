"""add valor_base to eventos

Revision ID: a1639b56b8fb
Revises: 67ad2a758bd4
Create Date: 2026-02-23
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1639b56b8fb'
down_revision = '67ad2a758bd4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'eventos',
        sa.Column('valor_base', sa.Numeric(10, 2), nullable=False, server_default='0')
    )


def downgrade():
    op.drop_column('eventos', 'valor_base')