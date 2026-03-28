"""Update tournaments

Revision ID: a5b2e54012eb
Revises: e52fa166371c
Create Date: 2026-03-28 17:12:10.347739

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a5b2e54012eb'
down_revision = 'e52fa166371c'
branch_labels = None
depends_on = None

external_id_unique_constraint_name = "uq_tournament_external_id"


def upgrade():
    op.create_unique_constraint('uq_tournament_name_org_start', 'tournament', ['name', 'organization_id', 'start_date'], schema='app')
    op.create_unique_constraint(external_id_unique_constraint_name, 'tournament', ['external_id'], schema='app')


def downgrade():
    op.drop_constraint('uq_tournament_name_org_start', 'tournament', schema='app', type_='unique')
    op.drop_constraint(external_id_unique_constraint_name, 'tournament', schema='app', type_='unique')
