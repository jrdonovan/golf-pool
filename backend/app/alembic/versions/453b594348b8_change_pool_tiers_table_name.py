"""Change pool tiers table name

Revision ID: 453b594348b8
Revises: 3a927243f836
Create Date: 2026-03-27 15:57:22.625393

"""
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = '453b594348b8'
down_revision = '3a927243f836'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("pooltier", schema="app")
    op.create_table('pool_tier',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('pool_id', sa.Uuid(), nullable=False),
    sa.Column('description', sa.Float(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['pool_id'], ['app.pool.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='app'
    )


def downgrade():
    op.drop_table("pool_tier", schema="app")
    op.create_table('pooltier',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('pool_id', sa.Uuid(), nullable=False),
    sa.Column('description', sa.Float(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['pool_id'], ['app.pool.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='app'
    )
