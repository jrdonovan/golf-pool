"""Initial schema

Revision ID: 7b4b3946b91f
Revises:
Create Date: 2026-03-31 18:20:07.962740

"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7b4b3946b91f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "course",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("external_id", sa.Integer(), nullable=True),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("city", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column(
            "state", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
        sa.Column(
            "country", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
        sa.Column("par_front_nine", sa.Integer(), nullable=True),
        sa.Column("par_back_nine", sa.Integer(), nullable=True),
        sa.Column("par_total", sa.Integer(), nullable=True),
        sa.Column("yardage_front_nine", sa.Integer(), nullable=True),
        sa.Column("yardage_back_nine", sa.Integer(), nullable=True),
        sa.Column("yardage_total", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )
    op.create_table(
        "organization",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("external_id", sa.Integer(), nullable=True),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id"),
        sa.UniqueConstraint("name"),
        schema="app",
    )
    op.create_table(
        "player",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("external_id", sa.Integer(), nullable=True),
        sa.Column(
            "first_name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
        sa.Column(
            "last_name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
        sa.Column(
            "country", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
        sa.Column("is_amateur", sa.Boolean(), nullable=True),
        sa.Column("birth_date", sa.DateTime(), nullable=True),
        sa.Column("world_ranking", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )
    op.create_table(
        "course_hole",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("hole_number", sa.Integer(), nullable=False),
        sa.Column("par", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["app.course.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )
    sa.Enum(
        "not_started",
        "in_progress",
        "complete",
        "official",
        name="tournamentstatus",
        schema="app",
    ).create(op.get_bind())
    op.create_table(
        "tournament",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("external_id", sa.Integer(), nullable=True),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("purse", sa.Integer(), nullable=True),
        sa.Column("format", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "not_started",
                "in_progress",
                "complete",
                "official",
                name="tournamentstatus",
                schema="app",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column(
            "timezone", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["app.organization.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "name", "organization_id", "start_date", name="uq_tournament_name_org_start"
        ),
        schema="app",
    )
    op.create_table(
        "player_tournament",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("player_id", sa.Uuid(), nullable=False),
        sa.Column("tournament_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("total_score", sa.Integer(), nullable=True),
        sa.Column("missed_cut", sa.Boolean(), nullable=False),
        sa.Column("withdrawn", sa.Boolean(), nullable=False),
        sa.Column("points", sa.Float(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["player_id"], ["app.player.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["tournament_id"], ["app.tournament.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )
    sa.Enum(
        "not_started",
        "in_progress",
        "complete",
        "closed",
        name="poolstatus",
        schema="app",
    ).create(op.get_bind())
    op.create_table(
        "pool",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tournament_id", sa.Uuid(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("entry_fee", sa.Float(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "not_started",
                "in_progress",
                "complete",
                "closed",
                name="poolstatus",
                schema="app",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tournament_id"], ["app.tournament.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )
    op.create_table(
        "tournament_course",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tournament_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["app.course.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["tournament_id"], ["app.tournament.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )
    op.create_table(
        "tournament_round",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tournament_id", sa.Uuid(), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tournament_id"], ["app.tournament.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )
    op.create_table(
        "player_round",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("player_tournament_id", sa.Uuid(), nullable=False),
        sa.Column("tournament_round_id", sa.Uuid(), nullable=False),
        sa.Column("tournament_course_id", sa.Uuid(), nullable=False),
        sa.Column("tee_time", sa.DateTime(), nullable=True),
        sa.Column("is_complete", sa.Boolean(), nullable=False),
        sa.Column("strokes", sa.Integer(), nullable=False),
        sa.Column("starting_hole", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["player_tournament_id"], ["app.player_tournament.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["tournament_course_id"], ["app.tournament_course.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["tournament_round_id"], ["app.tournament_round.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )
    op.create_table(
        "pool_tier",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("pool_id", sa.Uuid(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("description", sa.Float(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pool_id"], ["app.pool.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )
    op.create_table(
        "submission",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("pool_id", sa.Uuid(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column(
            "submitter_name",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=False,
        ),
        sa.Column(
            "submitter_email",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=False,
        ),
        sa.Column("total_score", sa.Float(), nullable=False),
        sa.Column("tiebreaker_strokes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pool_id"], ["app.pool.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )
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
        "player_hole",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("player_round_id", sa.Uuid(), nullable=False),
        sa.Column("course_hole_id", sa.Uuid(), nullable=False),
        sa.Column("strokes", sa.Integer(), nullable=False),
        sa.Column("score_to_par", sa.Integer(), nullable=False),
        sa.Column(
            "result",
            postgresql.ENUM(
                "condor",
                "albatross",
                "eagle",
                "birdie",
                "par",
                "bogey",
                "double_bogey",
                "triple_bogey_or_worse",
                name="holeresult",
                schema="app",
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column("is_playoff_hole", sa.Boolean(), nullable=False),
        sa.Column("play_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["course_hole_id"], ["app.course_hole.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["player_round_id"], ["app.player_round.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )
    op.create_table(
        "player_pool_tier",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("player_tournament_id", sa.Uuid(), nullable=False),
        sa.Column("pool_tier_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["player_tournament_id"], ["app.player_tournament.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["pool_tier_id"], ["app.pool_tier.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )
    op.create_table(
        "pick",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("submission_id", sa.Uuid(), nullable=False),
        sa.Column("player_pool_tier_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["player_pool_tier_id"],
            ["app.player_pool_tier.id"],
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["app.submission.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="app",
    )


def downgrade():
    op.drop_table("pick", schema="app")
    op.drop_table("player_pool_tier", schema="app")
    op.drop_table("player_hole", schema="app")
    op.drop_table("submission", schema="app")
    op.drop_table("pool_tier", schema="app")
    op.drop_table("player_round", schema="app")
    op.drop_table("tournament_round", schema="app")
    op.drop_table("tournament_course", schema="app")
    op.drop_table("pool", schema="app")
    op.drop_table("player_tournament", schema="app")
    op.drop_table("tournament", schema="app")
    op.drop_table("course_hole", schema="app")
    op.drop_table("player", schema="app")
    op.drop_table("organization", schema="app")
    op.drop_table("course", schema="app")
