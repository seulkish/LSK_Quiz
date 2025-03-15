# /app/models/quiz.py
# 퀴즈 모델

from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    questions_count = Column(Integer, default=10)  # 출제할 문제 수
    randomize_questions = Column(Boolean, default=True)  # 문제 순서 랜덤화 여부
    randomize_options = Column(Boolean, default=True)  # 선택지 순서 랜덤화 여부
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계 설정
    creator = relationship("User", backref="created_quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="quiz", cascade="all, delete-orphan")