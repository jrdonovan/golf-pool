"""Add player holes

Revision ID: 0feda0ca0b0f
Revises: 4f4e38e5c289
Create Date: 2026-03-28 10:26:11.160488

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0feda0ca0b0f'
down_revision = '4f4e38e5c289'
branch_labels = None
depends_on = None


def upgrade():
    sa.Enum(
        'condor',
        'albatross',
        'eagle',
        'birdie',
        'par',
        'bogey',
        'double_bogey',
        'triple_bogey_or_worse',
        name='holeresult',
        schema='app'
    ).create(op.get_bind())

    op.create_table(
        'player_hole',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('player_round_id', sa.Uuid(), nullable=False),
        sa.Column('course_hole_id', sa.Uuid(), nullable=False),
        sa.Column('strokes', sa.Integer(), nullable=False),
        sa.Column('score_to_par', sa.Integer(), nullable=False),
        sa.Column(
            'result',
            postgresql.ENUM(
                'condor',
                'albatross',
                'eagle',
                'birdie',
                'par',
                'bogey',
                'double_bogey',
                'triple_bogey_or_worse',
                name='holeresult',
                schema='app',
                create_type=False
            ),
            nullable=True
        ),
        sa.Column('is_playoff_hole', sa.Boolean(), nullable=False),
        sa.Column('play_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['course_hole_id'], ['app.course_hole.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['player_round_id'], ['app.player_round.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='app'
    )


def downgrade():
    op.drop_table('player_hole', schema='app')
    sa.Enum('condor', 'albatross', 'eagle', 'birdie', 'par', 'bogey', 'double_bogey', 'triple_bogey_or_worse', name='holeresult', schema='app').drop(op.get_bind())
