# app/schemas/quiz.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class QuestionBase(BaseModel):
    content: str
    options: List[str]
    correct_answer: int
    order: Optional[int] = None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    content: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[int] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class Question(QuestionBase):
    id: int
    quiz_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    questions_count: int = 10
    randomize_questions: bool = True
    randomize_options: bool = True


class QuizCreate(QuizBase):
    pass


class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    questions_count: Optional[int] = None
    randomize_questions: Optional[bool] = None
    randomize_options: Optional[bool] = None
    is_active: Optional[bool] = None


class Quiz(QuizBase):
    id: int
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuizWithQuestions(Quiz):
    questions: List[Question] = []