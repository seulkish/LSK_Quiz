# app/schemas/submission.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SubmissionAnswerBase(BaseModel):
    question_id: int
    selected_option: Optional[int] = None


class SubmissionAnswerCreate(SubmissionAnswerBase):
    pass


class SubmissionAnswer(SubmissionAnswerBase):
    id: int
    submission_id: int
    is_correct: Optional[bool] = None
    options_order: Optional[List[int]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubmissionBase(BaseModel):
    quiz_id: int
    user_id: int


class SubmissionCreate(SubmissionBase):
    question_order: List[int]


class SubmissionUpdate(BaseModel):
    submit_time: Optional[datetime] = None
    is_completed: Optional[bool] = None
    score: Optional[float] = None


class Submission(SubmissionBase):
    id: int
    start_time: datetime
    submit_time: Optional[datetime] = None
    question_order: List[int]
    score: Optional[float] = None
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubmissionWithAnswers(Submission):
    answers: List[SubmissionAnswer] = []