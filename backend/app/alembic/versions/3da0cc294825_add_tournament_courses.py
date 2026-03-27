"""Add tournament courses

Revision ID: 3da0cc294825
Revises: c7113a5e6080
Create Date: 2026-03-27 17:52:20.079167

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = '3da0cc294825'
down_revision = 'c7113a5e6080'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tournament_course',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tournament_id', sa.Uuid(), nullable=False),
        sa.Column('course_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['app.course.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tournament_id'], ['app.tournament.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='app'
    )


def downgrade():
    op.drop_table('tournament_course', schema='app')
