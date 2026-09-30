from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    conditions: Mapped[list["UserCondition"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="user"
    )


class HealthRule(Base):
    __tablename__ = "health_rules"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    condition_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True
    )

    condition_name: Mapped[str] = mapped_column(
        String(200)
    )

    high_risk_ingredients: Mapped[str] = mapped_column(
        Text
    )

    warning: Mapped[str] = mapped_column(
        Text
    )

    substitutions: Mapped[str] = mapped_column(
        Text
    )


class UserCondition(Base):
    __tablename__ = "user_conditions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    condition_id: Mapped[str] = mapped_column(
        ForeignKey("health_rules.condition_id"),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="conditions"
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "condition_id",
            name="unique_user_condition"
        ),
    )


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # The user who performed this analysis.
    # Nullable for now so existing analyses in the database
    # continue to work.
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    conditions: Mapped[str] = mapped_column(
        Text
    )

    ingredients: Mapped[str] = mapped_column(
        Text
    )

    safety_score: Mapped[float] = mapped_column(
        Float
    )

    status: Mapped[str] = mapped_column(
        String(100)
    )

    flagged_ingredients: Mapped[str] = mapped_column(
        Text
    )

    suggested_substitutions: Mapped[str] = mapped_column(
        Text
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    user: Mapped["User | None"] = relationship(
        back_populates="analyses"
    )