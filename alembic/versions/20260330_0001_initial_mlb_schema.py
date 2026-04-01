"""Initial MLB games + boxscore tables

Revision ID: 0001
Revises:
Create Date: 2026-03-30

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "games",
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("date_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("game_status", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("home_team", sa.String(), nullable=True),
        sa.Column("away_team", sa.String(), nullable=True),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("venue_name", sa.String(), nullable=True),
        sa.Column("venue_city", sa.String(), nullable=True),
        sa.Column("venue_state", sa.String(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("starting_pitchers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("opening_spread", sa.Float(), nullable=True),
        sa.Column("opening_total", sa.Float(), nullable=True),
        sa.Column("pickcenter", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("draftkings_lines", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("records_before_game", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("home_record", sa.String(), nullable=True),
        sa.Column("away_record", sa.String(), nullable=True),
        sa.Column("umpires", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("total_runs", sa.Integer(), nullable=True),
        sa.Column("margin", sa.Integer(), nullable=True),
        sa.Column("winner", sa.String(), nullable=True),
        sa.Column("loser", sa.String(), nullable=True),
        sa.Column("rl_winner", sa.String(), nullable=True),
        sa.Column("ou_result", sa.String(), nullable=True),
        sa.Column("ingested_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("game_id"),
    )
    op.create_index("ix_games_date_utc", "games", ["date_utc"], unique=False)
    op.create_index("ix_games_status", "games", ["status"], unique=False)
    op.create_index("ix_games_home_team", "games", ["home_team"], unique=False)
    op.create_index("ix_games_away_team", "games", ["away_team"], unique=False)
    op.create_index("ix_games_winner", "games", ["winner"], unique=False)

    op.create_table(
        "batting_lines",
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("team_name", sa.String(), nullable=True),
        sa.Column("player_id", sa.Integer(), nullable=True),
        sa.Column("player_name", sa.String(), nullable=True),
        sa.Column("stats", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    )
    op.create_index("ix_batting_lines_game_id", "batting_lines", ["game_id"], unique=False)

    op.create_table(
        "pitching_lines",
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("team_name", sa.String(), nullable=True),
        sa.Column("player_id", sa.Integer(), nullable=True),
        sa.Column("player_name", sa.String(), nullable=True),
        sa.Column("stats", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    )
    op.create_index("ix_pitching_lines_game_id", "pitching_lines", ["game_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_pitching_lines_game_id", table_name="pitching_lines")
    op.drop_table("pitching_lines")
    op.drop_index("ix_batting_lines_game_id", table_name="batting_lines")
    op.drop_table("batting_lines")
    op.drop_index("ix_games_winner", table_name="games")
    op.drop_index("ix_games_away_team", table_name="games")
    op.drop_index("ix_games_home_team", table_name="games")
    op.drop_index("ix_games_status", table_name="games")
    op.drop_index("ix_games_date_utc", table_name="games")
    op.drop_table("games")
