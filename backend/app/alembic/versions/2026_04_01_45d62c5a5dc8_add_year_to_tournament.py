"""Add year to tournament

Revision ID: 45d62c5a5dc8
Revises: 7b4b3946b91f
Create Date: 2026-04-01 10:52:35.634329

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = '45d62c5a5dc8'
down_revision = '7b4b3946b91f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'tournament',
        sa.Column('year', sa.Integer(), nullable=False),
        schema='app'
    )
    op.drop_constraint(
        op.f('uq_tournament_name_org_start'),
        'tournament',
        schema='app',
        type_='unique'
    )
    op.create_unique_constraint(
        'uq_tournament_name_org_year',
        'tournament',
        ['name', 'organization_id', 'year'],
        schema='app'
    )


def downgrade():
    op.drop_constraint(
        'uq_tournament_name_org_year', 'tournament',
        schema='app',
        type_='unique'
    )
    op.create_unique_constraint(
        op.f('uq_tournament_name_org_start'),
        'tournament',
        ['name', 'organization_id', 'start_date'],
        schema='app',
        postgresql_nulls_not_distinct=False
    )
    op.drop_column('tournament', 'year', schema='app')
