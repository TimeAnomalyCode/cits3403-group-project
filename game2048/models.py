from datetime import datetime, UTC
from game2048 import db
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint
from typing import Optional

# Relationships have backref
# Example
# 1. tableA has id, name
# 2. tableB has title, content
# 3. tableA has a relationship with tableB, which creates a link to tableA -> tableB
# 4. Backref(author) lets get tableA information from table B (tableA <- tableB)
# 5. tableA has id, name, posts(Relationship) | tableB has title, content, author(Backref)
# 6. The 2 new columns don't exist in the table but you can use it because the ORM is smart

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(60), nullable=False)
    image_file: Mapped[str] = mapped_column(String(20), nullable=False, default='default.jpg')

    otp_code = Relationship(
        "OTP",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
        uselist=False
    )

    match_entries = Relationship(
        "MatchPlayer",
        backref="user",
        lazy=True
    )

    matches_won = Relationship(
        "Match",
        foreign_keys="Tournament.host_user_id",
        backref="host",
        lazy=True
    )

    def __repr__(self):
        return f"User ('{self.id} {self.username} {self.email} {self.image_file}')"

class OTP(db.Model):
    __tablename__ = "OTP"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    otp_code: Mapped[int] = mapped_column(Integer(6), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now(UTC))

class Match(db.Model):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_code: Mapped[Optional[String]] = mapped_column(String(4), unique=True, nullable=True)

    # Tournament only
    tournament_id: Mapped[Optional[int]] = mapped_column(ForeignKey('tournaments.id'), nullable=True)
    round_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    match_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    winner_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='pending')

    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now(UTC), nullable=False)
    started_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)

    players = Relationship(
        "MatchPlayer",
        backref="match",
        lazy=True
    )

class MatchPlayer(db.Model):
    __tablename__ = "match_players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey('matches.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    placement: Mapped[int] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint('match.id', 'user_id', name='unique_match_player')
    )

class Tournament(db.Model):
    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tournament_code: Mapped[String] = mapped_column(String(12), unique=True, nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default='pending')
    host_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now(UTC), nullable=False)
    started_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)

    matches = Relationship(
        "Match",
        backref="tournament",
        lazy=True
    )

class Leaderboard(db.Model):
    __tablename__ = "leaderboard"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    matches_won: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user = Relationship(
        "User",
        backref="leaderboard_rank",
        uselist=False
    )