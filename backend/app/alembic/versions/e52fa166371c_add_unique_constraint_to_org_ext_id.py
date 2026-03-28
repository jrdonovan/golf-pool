"""Add unique constraint to org ext id

Revision ID: e52fa166371c
Revises: 0feda0ca0b0f
Create Date: 2026-03-28 16:04:07.225537

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = 'e52fa166371c'
down_revision = '0feda0ca0b0f'
branch_labels = None
depends_on = None

constraint_name = "uq_organization_external_id"

def upgrade():
    op.create_unique_constraint(constraint_name, 'organization', ['external_id'], schema='app')


def downgrade():
    op.drop_constraint(constraint_name, 'organization', schema='app', type_='unique')
