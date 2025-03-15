# /app/models/submission.py
# 제출 모델

from sqlalchemy import Boolean, Column, Integer, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    submit_time = Column(DateTime(timezone=True))  # 제출 시간
    question_order = Column(JSON)  # 출제된 문제의 순서 (JSON으로 저장)
    score = Column(Float)  # 점수
    is_completed = Column(Boolean, default=False)  # 완료 여부
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계 설정
    quiz = relationship("Quiz", back_populates="submissions")
    user = relationship("User", back_populates="submissions")
    answers = relationship("SubmissionAnswer", back_populates="submission", cascade="all, delete-orphan")


class SubmissionAnswer(Base):
    __tablename__ = "submission_answers"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option = Column(Integer)  # 사용자가 선택한 답안 인덱스
    is_correct = Column(Boolean)  # 정답 여부
    options_order = Column(JSON)  # 선택지 순서 (랜덤화된 경우 사용)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계 설정
    submission = relationship("Submission", back_populates="answers")
    question = relationship("Question", back_populates="answers")