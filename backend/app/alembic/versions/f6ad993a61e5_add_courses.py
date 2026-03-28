"""Add courses

Revision ID: f6ad993a61e5
Revises: 40cb2126f5c9
Create Date: 2026-03-27 17:31:22.531326

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = 'f6ad993a61e5'
down_revision = '40cb2126f5c9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'course',
        sa.Column('external_id', sa.Integer(), nullable=True),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('city', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('state', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('country', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('par_front_nine', sa.Integer(), nullable=True),
        sa.Column('par_back_nine', sa.Integer(), nullable=True),
        sa.Column('par_total', sa.Integer(), nullable=True),
        sa.Column('yardage_front_nine', sa.Integer(), nullable=True),
        sa.Column('yardage_back_nine', sa.Integer(), nullable=True),
        sa.Column('yardage_total', sa.Integer(), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='app'
    )


def downgrade():
    op.drop_table('course', schema='app')
