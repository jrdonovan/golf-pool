"""Add player rounds

Revision ID: 2977f3eaf1a9
Revises: 28f00de56a80
Create Date: 2026-03-28 09:50:39.008773

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = '2977f3eaf1a9'
down_revision = '28f00de56a80'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'player_round',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('player_tournament_id', sa.Uuid(), nullable=False),
        sa.Column('tournament_round_id', sa.Uuid(), nullable=False),
        sa.Column('tournament_course_id', sa.Uuid(), nullable=False),
        sa.Column('tee_time', sa.DateTime(), nullable=True),
        sa.Column('is_complete', sa.Boolean(), nullable=False),
        sa.Column('strokes', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['player_tournament_id'], ['app.player_tournament.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tournament_course_id'], ['app.tournament_course.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tournament_round_id'], ['app.tournament_round.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='app'
    )


def downgrade():
    op.drop_table('player_round', schema='app')
