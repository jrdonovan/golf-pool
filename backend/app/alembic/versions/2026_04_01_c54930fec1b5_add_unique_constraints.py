"""Add unique constraints

Revision ID: c54930fec1b5
Revises: 45d62c5a5dc8
Create Date: 2026-04-01 13:43:35.864469

"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "c54930fec1b5"
down_revision = "45d62c5a5dc8"
branch_labels = None
depends_on = None


def upgrade():
    sa.Enum(
        "stroke", "team", "team_match", "stableford", name="tournamentformat", schema="app"
    ).create(op.get_bind())
    op.add_column(
        "course",
        sa.Column(
            "live_golf_data_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        schema="app",
    )
    op.alter_column(
        "course",
        "city",
        existing_type=sa.VARCHAR(length=255),
        nullable=True,
        schema="app",
    )
    op.alter_column(
        "course",
        "state",
        existing_type=sa.VARCHAR(length=255),
        nullable=True,
        schema="app",
    )
    op.alter_column(
        "course",
        "country",
        existing_type=sa.VARCHAR(length=255),
        nullable=True,
        schema="app",
    )
    op.create_unique_constraint("uq_courses_live_golf_data_id_key", "course", ["live_golf_data_id"], schema="app")
    op.drop_column("course", "external_id", schema="app")

    op.create_unique_constraint(
        "uq_course_hole_number",
        "course_hole",
        ["course_id", "hole_number"],
        schema="app",
    )

    op.add_column(
        "organization",
        sa.Column(
            "live_golf_data_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        schema="app",
    )
    op.drop_constraint(
        op.f("organization_external_id_key"),
        "organization",
        schema="app",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_organizations_live_golf_data_id_key", "organization", ["live_golf_data_id"], schema="app"
    )
    op.drop_column("organization", "external_id", schema="app")

    op.create_unique_constraint(
        "uq_submission_player_pool_tier",
        "pick",
        ["submission_id", "player_pool_tier_id"],
        schema="app",
    )

    op.add_column(
        "player",
        sa.Column(
            "live_golf_data_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        schema="app",
    )
    op.alter_column(
        "player",
        "birth_date",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DATE(),
        existing_nullable=True,
        schema="app",
    )
    op.create_unique_constraint("uq_players_live_golf_data_id_key", "player", ["live_golf_data_id"], schema="app")
    op.drop_column("player", "external_id", schema="app")

    op.create_unique_constraint(
        "uq_player_hole_round_hole_order",
        "player_hole",
        ["player_round_id", "course_hole_id", "play_order"],
        schema="app",
    )

    op.create_unique_constraint(
        "uq_player_pool_tier_tournament_tier",
        "player_pool_tier",
        ["player_tournament_id", "pool_tier_id"],
        schema="app",
    )

    op.add_column(
        "player_round",
        sa.Column("score_to_par", sa.Integer(), nullable=False),
        schema="app",
    )
    op.create_unique_constraint(
        "uq_player_course_round",
        "player_round",
        ["player_tournament_id", "tournament_course_id", "tournament_round_id"],
        schema="app",
    )

    op.add_column(
        "player_tournament",
        sa.Column("strokes", sa.Integer(), nullable=True),
        schema="app",
    )
    op.add_column(
        "player_tournament",
        sa.Column("disqualified", sa.Boolean(), nullable=False),
        schema="app",
    )
    op.create_unique_constraint(
        "uq_player_tournament",
        "player_tournament",
        ["player_id", "tournament_id"],
        schema="app",
    )

    op.create_unique_constraint(
        "uq_name_tournament", "pool", ["name", "tournament_id"], schema="app"
    )

    op.alter_column(
        "pool_tier",
        "description",
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        type_=sqlmodel.sql.sqltypes.AutoString(length=255),
        existing_nullable=True,
        schema="app",
    )
    op.create_unique_constraint(
        "uq_pool_tiers_name_pool_id_key", "pool_tier", ["name", "pool_id"], schema="app"
    )

    op.alter_column(
        "submission",
        "tiebreaker_strokes",
        existing_type=sa.INTEGER(),
        nullable=False,
        schema="app",
    )
    op.create_unique_constraint(
        "uq_submissions_name_pool_id_key", "submission", ["name", "pool_id"], schema="app"
    )

    op.add_column(
        "tournament",
        sa.Column(
            "live_golf_data_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        schema="app",
    )
    op.alter_column(
        "tournament",
        "format",
        existing_type=sa.VARCHAR(),
        type_=sa.Enum(
            "stroke", "team", "team_match", "stableford", name="tournamentformat", schema="app"
        ),
        existing_nullable=True,
        schema="app",
        postgresql_using="format::app.tournamentformat",
    )
    op.alter_column(
        "tournament",
        "status",
        existing_type=postgresql.ENUM(
            "not_started",
            "in_progress",
            "complete",
            "official",
            name="tournamentstatus",
            schema="app",
        ),
        nullable=True,
        schema="app",
    )
    op.drop_column("tournament", "external_id", schema="app")

    op.create_unique_constraint(
        "uq_tournament_course",
        "tournament_course",
        ["tournament_id", "course_id"],
        schema="app",
    )

    op.create_unique_constraint(
        "uq_tournament_round",
        "tournament_round",
        ["tournament_id", "round_number"],
        schema="app",
    )


def downgrade():
    op.drop_constraint(
        "uq_tournament_round", "tournament_round", schema="app", type_="unique"
    )

    op.drop_constraint(
        "uq_tournament_course", "tournament_course", schema="app", type_="unique"
    )

    op.add_column(
        "tournament",
        sa.Column("external_id", sa.INTEGER(), autoincrement=False, nullable=True),
        schema="app",
    )
    op.alter_column(
        "tournament",
        "status",
        existing_type=postgresql.ENUM(
            "not_started",
            "in_progress",
            "complete",
            "official",
            name="tournamentstatus",
            schema="app",
        ),
        nullable=False,
        schema="app",
    )
    op.alter_column(
        "tournament",
        "format",
        existing_type=sa.Enum(
            "stroke", "team", "team_match", "stableford", name="tournamentformat"
        ),
        type_=sa.VARCHAR(),
        existing_nullable=True,
        schema="app",
    )
    op.drop_column("tournament", "live_golf_data_id", schema="app")

    op.drop_constraint("uq_submissions_name_pool_id_key", "submission", schema="app", type_="unique")
    op.alter_column(
        "submission",
        "tiebreaker_strokes",
        existing_type=sa.INTEGER(),
        nullable=True,
        schema="app",
    )

    op.drop_constraint("uq_pool_tiers_name_pool_id_key", "pool_tier", schema="app", type_="unique")
    op.alter_column(
        "pool_tier",
        "description",
        existing_type=sqlmodel.sql.sqltypes.AutoString(length=255),
        type_=sa.DOUBLE_PRECISION(precision=53),
        existing_nullable=True,
        schema="app",
    )

    op.drop_constraint("uq_name_tournament", "pool", schema="app", type_="unique")

    op.drop_constraint(
        "uq_player_tournament", "player_tournament", schema="app", type_="unique"
    )
    op.drop_column("player_tournament", "disqualified", schema="app")
    op.drop_column("player_tournament", "strokes", schema="app")

    op.drop_constraint(
        "uq_player_course_round", "player_round", schema="app", type_="unique"
    )
    op.drop_column("player_round", "score_to_par", schema="app")

    op.drop_constraint(
        "uq_player_pool_tier_tournament_tier",
        "player_pool_tier",
        schema="app",
        type_="unique",
    )

    op.drop_constraint(
        "uq_player_hole_round_hole_order", "player_hole", schema="app", type_="unique"
    )

    op.add_column(
        "player",
        sa.Column("external_id", sa.INTEGER(), autoincrement=False, nullable=True),
        schema="app",
    )
    op.drop_constraint("uq_players_live_golf_data_id_key", "player", schema="app", type_="unique")
    op.alter_column(
        "player",
        "birth_date",
        existing_type=sa.DATE(),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
        schema="app",
    )
    op.drop_column("player", "live_golf_data_id", schema="app")

    op.drop_constraint(
        "uq_submission_player_pool_tier", "pick", schema="app", type_="unique"
    )

    op.add_column(
        "organization",
        sa.Column("external_id", sa.INTEGER(), autoincrement=False, nullable=True),
        schema="app",
    )
    op.drop_constraint("uq_organizations_live_golf_data_id_key", "organization", schema="app", type_="unique")
    op.create_unique_constraint(
        op.f("organization_external_id_key"),
        "organization",
        ["external_id"],
        schema="app",
        postgresql_nulls_not_distinct=False,
    )
    op.drop_column("organization", "live_golf_data_id", schema="app")

    op.drop_constraint(
        "uq_course_hole_number", "course_hole", schema="app", type_="unique"
    )

    op.add_column(
        "course",
        sa.Column("external_id", sa.INTEGER(), autoincrement=False, nullable=True),
        schema="app",
    )
    op.drop_constraint("uq_courses_live_golf_data_id_key", "course", schema="app", type_="unique")
    op.alter_column(
        "course",
        "country",
        existing_type=sa.VARCHAR(length=255),
        nullable=False,
        schema="app",
    )
    op.alter_column(
        "course",
        "state",
        existing_type=sa.VARCHAR(length=255),
        nullable=False,
        schema="app",
    )
    op.alter_column(
        "course",
        "city",
        existing_type=sa.VARCHAR(length=255),
        nullable=False,
        schema="app",
    )
    op.drop_column("course", "live_golf_data_id", schema="app")

    sa.Enum("stroke", "team", "team_match", "stableford", name="tournamentformat", schema="app").drop(
        op.get_bind()
    )
