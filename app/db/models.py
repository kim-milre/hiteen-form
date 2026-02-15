from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from app.db.base import Base


class TemplateResponse(Base):
    __tablename__ = "template_responses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    student_id = Column(String, nullable=False)
    number = Column(String, nullable=False)
    major = Column(String, nullable=True)
    interest = Column(String, nullable=False)  # comma separated
    payment_status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())