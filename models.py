from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class HealthRule(Base):
    __tablename__ = "health_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    condition_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    condition_name: Mapped[str] = mapped_column(String(200))
    high_risk_ingredients: Mapped[str] = mapped_column(Text)
    warning: Mapped[str] = mapped_column(Text)
    substitutions: Mapped[str] = mapped_column(Text)

class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conditions: Mapped[str] = mapped_column(Text)
    ingredients: Mapped[str] = mapped_column(Text)
    safety_score: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(100))
    flagged_ingredients: Mapped[str] = mapped_column(Text)
    suggested_substitutions: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
