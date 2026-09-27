from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)

    description = Column(Text, nullable=False)

    severity = Column(String(20), default="medium")

    root_cause = Column(Text, nullable=True)

    resolution = Column(Text, nullable=True)

    outcome = Column(Text, nullable=True)

    status = Column(String(20), default="open")

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )