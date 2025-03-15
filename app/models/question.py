# /app/models/question.py
# 문제 모델

from sqlalchemy import Boolean, Column, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    content = Column(Text, nullable=False)  # 문제 내용
    options = Column(JSON, nullable=False)  # 선택지 목록 (JSON 형식)
    correct_answer = Column(Integer, nullable=False)  # 정답 인덱스
    order = Column(Integer)  # 문제 순서 (랜덤화 되지 않을 경우 사용)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계 설정
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("SubmissionAnswer", back_populates="question", cascade="all, delete-orphan")