"""Add course holes

Revision ID: c7113a5e6080
Revises: f6ad993a61e5
Create Date: 2026-03-27 17:42:27.958851

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c7113a5e6080'
down_revision = 'f6ad993a61e5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'course_hole',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('course_id', sa.Uuid(), nullable=False),
        sa.Column('hole_number', sa.Integer(), nullable=False),
        sa.Column('par', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['app.course.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='app'
    )


def downgrade():
    op.drop_table('course_hole', schema='app')
