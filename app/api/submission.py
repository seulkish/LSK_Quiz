# app/api/submission.py
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_current_user, get_current_admin, get_pagination_params
from app.db import get_db
from app.models.user import User
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.submission import Submission, SubmissionAnswer
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionUpdate,
    Submission as SubmissionSchema,
    SubmissionWithAnswers,
    SubmissionAnswerCreate
)

router = APIRouter()

# 제출 목록 조회 (관리자용)
@router.get("/", response_model=List[SubmissionSchema])
def read_submissions(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """모든 제출 목록 조회 (관리자용)"""
    submissions = db.query(Submission).offset(skip).limit(limit).all()
    return submissions

# 사용자별 제출 목록 조회
@router.get("/my", response_model=List[SubmissionSchema])
def read_user_submissions(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """현재 사용자의 제출 목록 조회"""
    submissions = db.query(Submission).filter(
        Submission.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return submissions

# 제출 기록 조회
@router.get("/{submission_id}", response_model=SubmissionWithAnswers)
def read_submission(
        *,
        db: Session = Depends(get_db),
        submission_id: int,
        current_user: User = Depends(get_current_user)
) -> Any:
    """특정 제출 기록 상세 조회"""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="제출 기록을 찾을 수 없습니다"
        )

    # 관리자 또는 본인의 제출만 조회 가능
    if not current_user.is_admin and submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 제출 기록에 접근할 권한이 없습니다"
        )

    return submission

# 답안 제출
@router.post("/{submission_id}/answers", status_code=status.HTTP_201_CREATED)
def submit_answers(
        *,
        db: Session = Depends(get_db),
        submission_id: int,
        answers: List[SubmissionAnswerCreate],
        current_user: User = Depends(get_current_user)
) -> Any:
    """답안 제출"""
    submission = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.user_id == current_user.id,
        Submission.is_completed == False
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유효한 응시 기록을 찾을 수 없거나 이미 완료된 시험입니다"
        )

    # 문제 정보 가져오기
    quiz = db.query(Quiz).filter(Quiz.id == submission.quiz_id).first()

    # 기존 답안 삭제
    db.query(SubmissionAnswer).filter(SubmissionAnswer.submission_id == submission_id).delete()

    # 새 답안 저장 및 채점
    correct_count = 0

    for answer in answers:
        question = db.query(Question).filter(Question.id == answer.question_id).first()

        if not question:
            continue

        is_correct = (answer.selected_option == question.correct_answer)
        if is_correct:
            correct_count += 1

        submission_answer = SubmissionAnswer(
            submission_id=submission_id,
            question_id=answer.question_id,
            selected_option=answer.selected_option,
            is_correct=is_correct
        )
        db.add(submission_answer)

    # 제출 정보 업데이트
    total_questions = len(submission.question_order)
    score = (correct_count / total_questions) * 100 if total_questions > 0 else 0

    submission.submit_time = datetime.now()
    submission.is_completed = True
    submission.score = score

    db.commit()

    return {"message": "답안이 성공적으로 제출되었습니다", "score": score}

# 진행 중인 제출 답안 저장 (새로고침 대비)
@router.post("/{submission_id}/save", status_code=status.HTTP_200_OK)
def save_progress(
        *,
        db: Session = Depends(get_db),
        submission_id: int,
        answers: List[SubmissionAnswerCreate],
        current_user: User = Depends(get_current_user)
) -> Any:
    """진행 중인 응시 상태 저장 (새로고침 대비)"""
    submission = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.user_id == current_user.id,
        Submission.is_completed == False
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유효한 응시 기록을 찾을 수 없거나 이미 완료된 시험입니다"
        )

    # 기존 답안 삭제
    db.query(SubmissionAnswer).filter(SubmissionAnswer.submission_id == submission_id).delete()

    # 새 답안 저장 (채점하지 않음)
    for answer in answers:
        submission_answer = SubmissionAnswer(
            submission_id=submission_id,
            question_id=answer.question_id,
            selected_option=answer.selected_option,
            is_correct=None  # 채점하지 않음
        )
        db.add(submission_answer)

    db.commit()

    return {"message": "응시 진행상황이 저장되었습니다"}