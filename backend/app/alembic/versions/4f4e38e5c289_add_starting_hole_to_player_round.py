"""Add starting_hole to player round

Revision ID: 4f4e38e5c289
Revises: 2977f3eaf1a9
Create Date: 2026-03-28 10:20:28.513399

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = '4f4e38e5c289'
down_revision = '2977f3eaf1a9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'player_round',
        sa.Column('starting_hole', sa.Integer(), nullable=False),
        schema='app'
    )


def downgrade():
    op.drop_column('player_round', 'starting_hole', schema='app')
