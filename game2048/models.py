from datetime import datetime, UTC
from game2048 import db
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash

# Relationships have backref (Same concept with back_populates but you have to write for both table)
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
        back_populates="user",
        uselist=False
    )

    match_entries = Relationship(
        "MatchPlayer",
        back_populates="user"
    )

    # tournaments this user is hosting
    hosted_tournaments = Relationship(
        "Tournament",
        foreign_keys="Tournament.host_user_id",
        back_populates="host"
    )

    # matches this user has won
    wins = Relationship(
        "Match",
        foreign_keys="Match.winner_id",
        back_populates="winner"
    )

    leaderboard_rank = Relationship(
        "Leaderboard",
        back_populates="user",
        uselist=False
    )

    # Prints out all column names and variables for debugging
    def __repr__(self):
        return f'{self.__tablename__} = ' + ' | '.join(
            f'{col.name}: {getattr(self, col.name)}' for col in self.__table__.columns
        )

class OTP(db.Model):
    __tablename__ = "otp"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    otp_code: Mapped[str] = mapped_column(String(6), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    user = Relationship(
        "User",
        back_populates="otp_code",
        uselist=False
    )

    # Prints out all column names and variables
    def __repr__(self):
        return f'{self.__tablename__} = ' + ' | '.join(
            f'{col.name}: {getattr(self, col.name)}' for col in self.__table__.columns
        )

class Match(db.Model):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_code: Mapped[String | None] = mapped_column(String(4), unique=True, nullable=True)

    # Tournament only
    tournament_id: Mapped[int | None] = mapped_column(ForeignKey('tournaments.id'), nullable=True)
    round_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    match_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    winner_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='pending')

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    players = Relationship(
        "MatchPlayer",
        back_populates="match",
        cascade="all, delete-orphan"
    )

    tournament = Relationship(
        "Tournament",
        back_populates="matches"
    )

    winner = Relationship(
        "User",
        foreign_keys=[winner_id],
        back_populates="wins"
    )

    # Prints out all column names and variables
    def __repr__(self):
        return f'{self.__tablename__} = ' + ' | '.join(
            f'{col.name}: {getattr(self, col.name)}' for col in self.__table__.columns
        )

class MatchPlayer(db.Model):
    __tablename__ = "match_players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey('matches.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    placement: Mapped[int] = mapped_column(Integer, nullable=True)

    match = Relationship(
        "Match",
        back_populates="players"
    )

    user = Relationship(
        "User",
        back_populates="match_entries"
    )

    __table_args__ = (
        UniqueConstraint('match_id', 'user_id', name='unique_match_player'),
    )

    # Prints out all column names and variables
    def __repr__(self):
        return f'{self.__tablename__} = ' + ' | '.join(
            f'{col.name}: {getattr(self, col.name)}' for col in self.__table__.columns
        )

class Tournament(db.Model):
    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tournament_code: Mapped[String] = mapped_column(String(12), unique=True, nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default='pending')
    host_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    matches = Relationship(
        "Match",
        back_populates="tournament",
        cascade="all, delete-orphan"
    )

    host = Relationship(
        "User",
        back_populates="hosted_tournaments",
        foreign_keys=[host_user_id]
    )

    # Prints out all column names and variables
    def __repr__(self):
        return f'{self.__tablename__} = ' + ' | '.join(
            f'{col.name}: {getattr(self, col.name)}' for col in self.__table__.columns
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
        back_populates="leaderboard_rank",
        uselist=False
    )

    # Prints out all column names and variables
    def __repr__(self):
        return f'{self.__tablename__} = ' + ' | '.join(
            f'{col.name}: {getattr(self, col.name)}' for col in self.__table__.columns
        )