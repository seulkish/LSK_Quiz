# app/services/quiz.py
from typing import List, Optional, Dict, Any
import random
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.quiz import Quiz
from app.models.question import Question
from app.models.submission import Submission, SubmissionAnswer
from app.models.user import User
from app.schemas.quiz import QuizCreate, QuestionCreate, QuizUpdate

class QuizService:
    @staticmethod
    def create_quiz(db: Session, quiz_in: QuizCreate, user_id: int) -> Quiz:
        """퀴즈 생성"""
        quiz = Quiz(
            title=quiz_in.title,
            description=quiz_in.description,
            questions_count=quiz_in.questions_count,
            randomize_questions=quiz_in.randomize_questions,
            randomize_options=quiz_in.randomize_options,
            created_by=user_id
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        return quiz

    @staticmethod
    def get_quizzes(db: Session, skip: int = 0, limit: int = 100, user: Optional[User] = None) -> List[Quiz]:
        """퀴즈 목록 조회"""
        # 관리자는 모든 퀴즈 볼 수 있음
        if user and user.is_admin:
            return db.query(Quiz).offset(skip).limit(limit).all()
        # 일반 사용자는 활성화된 퀴즈만 볼 수 있음
        return db.query(Quiz).filter(Quiz.is_active == True).offset(skip).limit(limit).all()

    @staticmethod
    def get_quiz(db: Session, quiz_id: int) -> Optional[Quiz]:
        """퀴즈 상세 정보 조회"""
        return db.query(Quiz).filter(Quiz.id == quiz_id).first()

    @staticmethod
    def update_quiz(db: Session, quiz_id: int, quiz_in: QuizUpdate) -> Optional[Quiz]:
        """퀴즈 수정"""
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            return None

        update_data = quiz_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(quiz, field, value)

        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        return quiz

    @staticmethod
    def delete_quiz(db: Session, quiz_id: int) -> bool:
        """퀴즈 삭제"""
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            return False

        db.delete(quiz)
        db.commit()
        return True

    @staticmethod
    def create_question(db: Session, quiz_id: int, question_in: QuestionCreate) -> Optional[Question]:
        """문제 생성"""
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            return None

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

    @staticmethod
    def get_random_questions(db: Session, quiz_id: int, count: int) -> List[Question]:
        """퀴즈에서 랜덤 문제 선택"""
        all_questions = db.query(Question).filter(
            Question.quiz_id == quiz_id,
            Question.is_active == True
        ).all()

        # 문제 수가 요청 수보다 적으면 모든 문제 반환
        if len(all_questions) <= count:
            return all_questions

        # 랜덤하게 문제 선택
        return random.sample(all_questions, count)

    @staticmethod
    def get_or_create_submission(db: Session, quiz_id: int, user_id: int) -> Submission:
        """응시 정보 조회 또는 생성"""
        # 진행 중인 응시 기록 조회
        submission = db.query(Submission).filter(
            Submission.quiz_id == quiz_id,
            Submission.user_id == user_id,
            Submission.is_completed == False
        ).first()

        # 진행 중인 응시가 없으면 새로 생성
        if not submission:
            quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
            if not quiz:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="퀴즈를 찾을 수 없습니다"
                )

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
                user_id=user_id,
                question_order=question_ids,
                is_completed=False
            )
            db.add(submission)
            db.commit()
            db.refresh(submission)

        return submission

    @staticmethod
    def get_questions_for_page(db: Session, submission: Submission, quiz: Quiz, page: int) -> List[Dict[str, Any]]:
        """페이지에 맞는 문제 목록 조회"""
        # 한 페이지당 문제 수 계산
        questions_per_page = quiz.questions_count // 3 if quiz.questions_count >= 3 else quiz.questions_count
        total_pages = (len(submission.question_order) + questions_per_page - 1) // questions_per_page

        # 페이지 번호 유효성 검사
        if page > total_pages:
            page = total_pages
        if page < 1:
            page = 1

        # 현재 페이지에 해당하는 문제 인덱스 계산
        start_idx = (page - 1) * questions_per_page
        end_idx = min(start_idx + questions_per_page, len(submission.question_order))

        # 현재 페이지에 해당하는 문제 ID 추출
        current_question_ids = submission.question_order[start_idx:end_idx]

        # 결과 목록
        results = []

        # 이미 제출한 답변이 있는지 확인
        submitted_answers = {
            ans.question_id: ans.selected_option
            for ans in db.query(SubmissionAnswer).filter(
                SubmissionAnswer.submission_id == submission.id
            ).all()
        }

        # 해당 문제들 조회
        for q_id in current_question_ids:
            question = db.query(Question).filter(Question.id == q_id).first()
            if not question:
                continue

            # 문제 기본 정보
            question_data = {
                "id": question.id,
                "content": question.content,
                "options": question.options.copy(),
                "correct_answer": question.correct_answer
            }

            # 선택지 순서 랜덤화 처리
            if quiz.randomize_options:
                # 원래 정답 선택지 기억
                correct_option = question.options[question.correct_answer]
                # 선택지 섞기
                options = question.options.copy()
                random.shuffle(options)
                # 새로운 정답 인덱스 찾기
                new_correct_idx = options.index(correct_option)
                question_data["options"] = options
                question_data["correct_answer"] = new_correct_idx

            # 이미 제출한 답변이 있으면 추가
            if q_id in submitted_answers:
                question_data["selected_option"] = submitted_answers[q_id]

            results.append(question_data)

        return results