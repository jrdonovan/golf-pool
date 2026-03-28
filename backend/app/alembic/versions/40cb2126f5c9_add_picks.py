"""Add picks

Revision ID: 40cb2126f5c9
Revises: 2e2ad08515a3
Create Date: 2026-03-27 17:13:30.285609

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = '40cb2126f5c9'
down_revision = '2e2ad08515a3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pick',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('submission_id', sa.Uuid(), nullable=False),
        sa.Column('player_pool_tier_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['player_pool_tier_id'], ['app.player_pool_tier.id'],),
        sa.ForeignKeyConstraint(['submission_id'], ['app.submission.id'],),
        sa.PrimaryKeyConstraint('id'),
        schema='app'
    )


def downgrade():
    op.drop_table('pick', schema='app')
