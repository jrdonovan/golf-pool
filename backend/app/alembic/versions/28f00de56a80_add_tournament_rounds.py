"""Add tournament rounds

Revision ID: 28f00de56a80
Revises: 3da0cc294825
Create Date: 2026-03-28 09:37:14.201577

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = '28f00de56a80'
down_revision = '3da0cc294825'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tournament_round',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tournament_id', sa.Uuid(), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tournament_id'], ['app.tournament.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='app'
    )


def downgrade():
    op.drop_table('tournament_round', schema='app')
