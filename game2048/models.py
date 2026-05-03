from datetime import datetime, UTC
from time import time
from game2048 import app, db, login_manager
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import jwt

# Relationships have backref (Same concept with back_populates but you have to write for both table)
# Example
# 1. tableA has id, name
# 2. tableB has title, content
# 3. tableA has a relationship with tableB, which creates a link to tableA -> tableB
# 4. Backref(author) lets get tableA information from table B (tableA <- tableB)
# 5. tableA has id, name, posts(Relationship) | tableB has title, content, author(Backref)
# 6. The 2 new columns don't exist in the table but you can use it because the ORM is smart


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(60), nullable=False)
    profile_pic: Mapped[str] = mapped_column(String(225), nullable=False)
    elo: Mapped[int] = mapped_column(Integer, nullable=False, default=700)

    # User table relationships
    wins = Relationship(
        "Match", foreign_keys="Match.winner_id", back_populates="winner"
    )

    player1_in_matches = Relationship(
        "Match", foreign_keys="Match.player1_id", back_populates="player1"
    )

    player2_in_matches = Relationship(
        "Match", foreign_keys="Match.player2_id", back_populates="player2"
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    # Let the Class verify the token by using static
    # return None if the decode fails
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])[
                "reset_password"
            ]

        except:
            return

        return db.session.get(User, id)

    # Prints out all column names and variables for debugging
    def __repr__(self):
        return f"{self.__tablename__} = " + " | ".join(
            f"{col.name}: {getattr(self, col.name)}" for col in self.__table__.columns
        )


class Match(db.Model):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_code: Mapped[String | None] = mapped_column(
        String(4), unique=True, nullable=True
    )
    player1_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    player2_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    winner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    player1_elo: Mapped[int] = mapped_column(Integer, nullable=False)
    player2_elo: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )

    # Matches relationships
    player1 = Relationship(
        "User", foreign_keys=[player1_id], back_populates="player1_in_matches"
    )
    player2 = Relationship(
        "User", foreign_keys=[player2_id], back_populates="player2_in_matches"
    )
    winner = Relationship("User", foreign_keys=[winner_id], back_populates="wins")


# User Loader Function
@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))
