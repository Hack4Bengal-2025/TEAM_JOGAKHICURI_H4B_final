from typing import Optional
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs
from app.utils import PasswordManager


Base = declarative_base(cls=AsyncAttrs)

category_note_association_table = sa.Table(
    "category_note_association",
    Base.metadata,
    sa.Column(
        "category_id", sa.Integer, sa.ForeignKey("categories.id"), primary_key=True
    ),
    sa.Column("note_id", sa.Integer, sa.ForeignKey(
        "notes.id"), primary_key=True),
)

private_shares_association_table = sa.Table(
    "private_shares_association",
    Base.metadata,
    sa.Column("user_id", sa.Integer, sa.ForeignKey(
        "users.id"), primary_key=True),
    sa.Column("note_id", sa.Integer, sa.ForeignKey(
        "notes.id"), primary_key=True),
)


class PublicShares(Base):
    __tablename__ = "public_shares"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    uuid = sa.Column(sa.String(64), unique=True, index=True)
    note_id = sa.Column(
        sa.Integer, sa.ForeignKey("notes.id"), nullable=False, index=True
    )
    shared_at = sa.Column(sa.DateTime, default=datetime.now())


class BaseDBModel(Base):
    __abstract__ = True

    created_at = sa.Column(sa.DateTime, default=datetime.now())
    updated_at = sa.Column(
        sa.DateTime, default=datetime.now(), onupdate=datetime.now())
    is_active = sa.Column(sa.BOOLEAN, default=True)
    is_deleted = sa.Column(sa.BOOLEAN, default=False)

    def to_dict(
        self, *, exclude: Optional[list] = None, only: Optional[list] = None
    ) -> dict:
        if only is not None:
            return {
                c.name: getattr(self, c.name)
                for c in self.__table__.columns
                if c.name in exclude
            }
        if exclude is not None:
            return {
                c.name: getattr(self, c.name)
                for c in self.__table__.columns
                if c.name not in exclude
            }
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(BaseDBModel):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    first_name = sa.Column(sa.String(150), nullable=False)
    last_name = sa.Column(sa.String(150), nullable=True)
    email = sa.Column(sa.String(255), nullable=False, unique=True, index=True)
    username = sa.Column(sa.String(50), unique=True, index=True)
    password_hash = sa.Column(sa.String(100), nullable=False)
    dob = sa.Column(sa.Date)
    profile_pic = sa.Column(sa.String(255))
    is_validated = sa.Column(sa.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, value: str):
        self.password_hash = PasswordManager.hash_password(value)

    def verify_password(self, password: str) -> bool:
        return PasswordManager.verify_password(password, self.password_hash)


class File(BaseDBModel):
    __tablename__ = "files"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(64), nullable=False, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    file_path = sa.Column(sa.String(64), nullable=False)
    mimetype = sa.Column(sa.String(128), nullable=False)
    sha256 = sa.Column(sa.String(128), index=True, nullable=True)
    is_processed = sa.Column(sa.Boolean, default=False)
    uploaded_by = sa.Column(
        sa.Integer, sa.ForeignKey("users.id"), nullable=False)


class Collection(BaseDBModel):
    __tablename__ = "collections"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String(255), unique=False, index=True)
    is_ai_generated = sa.Column(sa.Boolean, default=False)
    creator_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.id"), nullable=True, index=True
    )

    notes = relationship("Note", back_populates="collection", lazy="selectin")
    quizzes = relationship(
        "Quiz", back_populates="collection", lazy="selectin")


class Category(BaseDBModel):
    __tablename__ = "categories"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String(255), unique=False, index=True)
    color = sa.Column(sa.String(7), nullable=True, default="#000000")
    icon = sa.Column(sa.String(255), nullable=True)
    is_ai_generated = sa.Column(sa.Boolean, default=False)
    creator_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.id"), nullable=True, index=True
    )

    notes = relationship(
        "Note", secondary=category_note_association_table, lazy="selectin")


class Note(BaseDBModel):
    __tablename__ = "notes"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String(255), unique=False)
    content = sa.Column(sa.Text)
    is_ai_generated = sa.Column(sa.Boolean, default=False)
    collection_id = sa.Column(
        sa.Integer, sa.ForeignKey("collections.id"), nullable=True, index=True
    )
    creator_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.id"), nullable=True, index=True
    )

    categories = relationship(
        "Category", secondary=category_note_association_table, back_populates="notes", lazy="selectin"
    )

    collection = relationship(
        "Collection", back_populates="notes", lazy="selectin")


class Quiz(BaseDBModel):
    __tablename__ = "quizzes"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String(255), unique=False)
    content = sa.Column(sa.Text)
    is_ai_generated = sa.Column(sa.Boolean, default=False)
    collection_id = sa.Column(
        sa.Integer, sa.ForeignKey("collections.id"), nullable=True, index=True
    )
    creator_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.id"), nullable=True, index=True
    )

    collection = relationship(
        "Collection", back_populates="quizzes", lazy="selectin")
    questions = relationship(
        "QuizQuestion", back_populates="quiz", lazy="selectin")


class QuizQuestion(BaseDBModel):
    __tablename__ = "quiz_questions"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    question_type = sa.Column(sa.String(50), nullable=False)
    question = sa.Column(sa.Text, nullable=True)
    options = sa.Column(sa.JSON, nullable=False, server_default='[]')
    answer = sa.Column(sa.JSON, nullable=False, server_default='""')
    quiz_id = sa.Column(
        sa.Integer, sa.ForeignKey("quizzes.id"), nullable=True, index=True
    )
    creator_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.id"), nullable=True, index=True
    )
    is_ai_generated = sa.Column(sa.Boolean, default=False)

    quiz = relationship("Quiz", back_populates="questions", lazy="selectin")


class FlashCard(BaseDBModel):
    __tablename__ = "flashcards"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    question = sa.Column(sa.Text, nullable=False)
    answer = sa.Column(sa.Text, nullable=False)
    is_ai_generated = sa.Column(sa.Boolean, default=False)
    collection_id = sa.Column(
        sa.Integer, sa.ForeignKey("collections.id"), nullable=True, index=True
    )
    creator_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.id"), nullable=True, index=True
    )

    repetition_count = sa.Column(
        sa.Integer,
        nullable=False,
        default=0,
        comment="How many times this card has been reviewed",
    )
    easiness_factor = sa.Column(
        sa.Float,
        nullable=False,
        default=2.5,
        comment="SM‑2 EF; higher means easier to remember",
    )
    interval_days = sa.Column(
        sa.Integer,
        nullable=False,
        default=0,
        comment="Current interval until next review (in days)",
    )
    last_reviewed = sa.Column(
        sa.DateTime, nullable=True, comment="Timestamp of the most recent review"
    )
    next_review_due = sa.Column(
        sa.DateTime,
        nullable=True,
        index=True,
        comment="Computed date when card should next surface",
    )

    collection = relationship("Collection", viewonly=True, lazy="selectin")

    def schedule_review(self, quality: int):
        """
        Apply the SM‑2 algorithm to update this card's scheduling metadata
        based on a user's self-graded quality (0–5).
        """
        if quality < 3:
            self.repetition_count = 0
            self.interval_days = 1
        else:
            self.repetition_count += 1
            if self.repetition_count == 1:
                self.interval_days = 1
            elif self.repetition_count == 2:
                self.interval_days = 6
            else:
                self.interval_days = int(
                    self.interval_days * self.easiness_factor)

            new_ef = self.easiness_factor + (
                0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
            )
            self.easiness_factor = max(new_ef, 1.3)

        now = datetime.now(timezone.utc)
        self.last_reviewed = now
        self.next_review_due = now + timedelta(days=self.interval_days)
