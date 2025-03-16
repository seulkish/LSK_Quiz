# app/api/quiz.py
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import random

from app.api.deps import get_current_admin, get_current_user, get_pagination_params
from app.db import get_db
from app.models.user import User
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.submission import Submission
from app.schemas.quiz import (
    QuizCreate,
    QuizUpdate,
    Quiz as QuizSchema,
    QuizWithQuestions,
    QuestionCreate,
    Question as QuestionSchema
)

router = APIRouter()

# 퀴즈 생성 (관리자만)
@router.post("/", response_model=QuizSchema, status_code=status.HTTP_201_CREATED)
def create_quiz(
        *,
        db: Session = Depends(get_db),
        quiz_in: QuizCreate,
        current_user: User = Depends(get_current_admin)
) -> Any:
    """퀴즈 생성 (관리자 전용)"""
    quiz = Quiz(
        title=quiz_in.title,
        description=quiz_in.description,
        questions_count=quiz_in.questions_count,
        randomize_questions=quiz_in.randomize_questions,
        randomize_options=quiz_in.randomize_options,
        created_by=current_user.id
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz

# 퀴즈 목록 조회
@router.get("/", response_model=List[QuizSchema])
def read_quizzes(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        page: int = Query(1, ge=1, description="페이지 번호"),
        page_size: int = Query(10, ge=1, le=100, description="페이지 크기")
) -> Any:
    """모든 퀴즈 목록 조회 (관리자는 모든 퀴즈, 일반 사용자는 응시 가능한 퀴즈)"""
    pagination = get_pagination_params(page, page_size)

    if current_user.is_admin:
        quizzes = db.query(Quiz).filter(Quiz.is_active == True) \
            .offset(pagination["skip"]).limit(pagination["limit"]).all()
    else:
        # 일반 사용자는 퀴즈 목록 조회 시 응시 여부 확인
        quizzes = db.query(Quiz).filter(Quiz.is_active == True) \
            .offset(pagination["skip"]).limit(pagination["limit"]).all()

    return quizzes

# 퀴즈 상세 조회
@router.get("/{quiz_id}", response_model=QuizWithQuestions)
def read_quiz(
        *,
        db: Session = Depends(get_db),
        quiz_id: int,
        current_user: User = Depends(get_current_user)
) -> Any:
    """특정 퀴즈의 상세 정보 조회"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.is_active == True).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="퀴즈를 찾을 수 없습니다"
        )
    return quiz

# 퀴즈 수정 (관리자만)
@router.put("/{quiz_id}", response_model=QuizSchema)
def update_quiz(
        *,
        db: Session = Depends(get_db),
        quiz_id: int,
        quiz_in: QuizUpdate,
        current_user: User = Depends(get_current_admin)
) -> Any:
    """퀴즈 정보 수정 (관리자 전용)"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="퀴즈를 찾을 수 없습니다"
        )

    update_data = quiz_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(quiz, field, value)

    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz

# 퀴즈 삭제 (관리자만)
@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
        *,
        db: Session = Depends(get_db),
        quiz_id: int,
        current_user: User = Depends(get_current_admin)
) -> None:
    """퀴즈 삭제 (관리자 전용)"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="퀴즈를 찾을 수 없습니다"
        )
    db.delete(quiz)
    db.commit()

# 문제 생성 (관리자만)
@router.post("/{quiz_id}/questions", response_model=QuestionSchema)
def create_question(
        *,
        db: Session = Depends(get_db),
        quiz_id: int,
        question_in: QuestionCreate,
        current_user: User = Depends(get_current_admin)
) -> Any:
    """퀴즈에 문제 추가 (관리자 전용)"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="퀴즈를 찾을 수 없습니다"
        )

        # 선택지 검증 - 최소 2개 이상
    if len(question_in.options) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="선택지는 최소 2개 이상이어야 합니다"
        )

    # 정답 인덱스 검증
    if question_in.correct_answer >= len(question_in.options):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="정답 인덱스가 유효하지 않습니다"
        )

    # 새 문제 생성
    question = Question(
        quiz_id=quiz_id,
        content=question_in.content,
        options=question_in.options,
        correct_answer=question_in.correct_answer,
        order=question_in.order
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

# 퀴즈 응시 (문제 조회 - 랜덤 선택)
@router.get("/{quiz_id}/take", response_model=List[QuestionSchema])
def take_quiz(
        *,
        db: Session = Depends(get_db),
        quiz_id: int,
        current_user: User = Depends(get_current_user),
        page: int = Query(1, ge=1, description="페이지 번호")
) -> Any:
    """퀴즈 응시를 위한 문제 조회 (페이지네이션 적용)"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.is_active == True).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="퀴즈를 찾을 수 없습니다"
        )

    # 응시 기록 확인 또는 생성
    submission = db.query(Submission).filter(
        Submission.quiz_id == quiz_id,
        Submission.user_id == current_user.id,
        Submission.is_completed == False
    ).first()

    if not submission:
        # 전체 문제 가져오기
        all_questions = db.query(Question).filter(
            Question.quiz_id == quiz_id,
            Question.is_active == True
        ).all()

        # 랜덤 문제 선택
        if quiz.randomize_questions and len(all_questions) > quiz.questions_count:
            selected_questions = random.sample(all_questions, quiz.questions_count)
            question_ids = [q.id for q in selected_questions]
        else:
            question_ids = [q.id for q in all_questions[:quiz.questions_count]]

        # 새 응시 기록 생성
        submission = Submission(
            quiz_id=quiz_id,
            user_id=current_user.id,
            question_order=question_ids,
            is_completed=False
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

    # 문제 페이징 처리
    questions_per_page = quiz.questions_count // 3 if quiz.questions_count >= 3 else quiz.questions_count
    total_pages = (len(submission.question_order) + questions_per_page - 1) // questions_per_page

    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * questions_per_page
    end_idx = min(start_idx + questions_per_page, len(submission.question_order))

    # 현재 페이지에 해당하는 문제 ID 추출
    current_question_ids = submission.question_order[start_idx:end_idx]

    # 해당 문제들 조회
    questions = []
    for q_id in current_question_ids:
        question = db.query(Question).filter(Question.id == q_id).first()
        if question:
            # 선택지 순서 랜덤화 처리
            question_data = QuestionSchema.from_orm(question)
            if quiz.randomize_options:
                # 원래 정답 인덱스 기억
                correct_option = question.options[question.correct_answer]
                # 선택지 섞기
                options = question.options.copy()
                random.shuffle(options)
                # 새로운 정답 인덱스 찾기
                new_correct_idx = options.index(correct_option)
                question_data.options = options
                question_data.correct_answer = new_correct_idx
            questions.append(question_data)

    return questions