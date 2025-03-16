# app/services/submission.py
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.quiz import Quiz
from app.models.question import Question
from app.models.submission import Submission, SubmissionAnswer
from app.models.user import User
from app.schemas.submission import SubmissionAnswerCreate

class SubmissionService:
    @staticmethod
    def get_submissions(db: Session, skip: int = 0, limit: int = 100) -> List[Submission]:
        """모든 제출 목록 조회"""
        return db.query(Submission).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_submissions(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Submission]:
        """사용자별 제출 목록 조회"""
        return db.query(Submission).filter(
            Submission.user_id == user_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_submission(db: Session, submission_id: int) -> Optional[Submission]:
        """제출 상세 정보 조회"""
        return db.query(Submission).filter(Submission.id == submission_id).first()

    @staticmethod
    def submit_answers(
            db: Session,
            submission_id: int,
            user_id: int,
            answers: List[SubmissionAnswerCreate]
    ) -> Tuple[bool, float]:
        """답안 제출 및 채점"""
        # 응시 정보 조회
        submission = db.query(Submission).filter(
            Submission.id == submission_id,
            Submission.user_id == user_id,
            Submission.is_completed == False
        ).first()

        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="유효한 응시 기록을 찾을 수 없거나 이미 완료된 시험입니다"
            )

        # 기존 답안 삭제
        db.query(SubmissionAnswer).filter(SubmissionAnswer.submission_id == submission_id).delete()

        # 새 답안 저장 및 채점
        correct_count = 0
        total_questions = len(submission.question_order)

        for answer in answers:
            question = db.query(Question).filter(Question.id == answer.question_id).first()

            if not question:
                continue

            # 정답 체크
            is_correct = (answer.selected_option == question.correct_answer)
            if is_correct:
                correct_count += 1

            # 답안 저장
            submission_answer = SubmissionAnswer(
                submission_id=submission_id,
                question_id=answer.question_id,
                selected_option=answer.selected_option,
                is_correct=is_correct
            )
            db.add(submission_answer)

        # 점수 계산
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0

        # 제출 정보 업데이트
        submission.submit_time = datetime.now()
        submission.is_completed = True
        submission.score = score

        db.commit()

        return True, score

    @staticmethod
    def save_progress(
            db: Session,
            submission_id: int,
            user_id: int,
            answers: List[SubmissionAnswerCreate]
    ) -> bool:
        """진행 중인 응시 상태 저장"""
        # 응시 정보 조회
        submission = db.query(Submission).filter(
            Submission.id == submission_id,
            Submission.user_id == user_id,
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
        return True

    @staticmethod
    def get_submission_result(db: Session, submission_id: int) -> Dict[str, Any]:
        """제출 결과 조회 - 상세 채점 내용 포함"""
        submission = db.query(Submission).filter(
            Submission.id == submission_id,
            Submission.is_completed == True
        ).first()

        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="완료된 응시 기록을 찾을 수 없습니다"
            )

        # 퀴즈 정보 조회
        quiz = db.query(Quiz).filter(Quiz.id == submission.quiz_id).first()

        # 답안 정보 조회
        answers = db.query(SubmissionAnswer).filter(
            SubmissionAnswer.submission_id == submission_id
        ).all()

        # 상세 정보 수집
        answer_details = []
        for answer in answers:
            question = db.query(Question).filter(Question.id == answer.question_id).first()
            if question:
                answer_details.append({
                    "question_id": question.id,
                    "question_content": question.content,
                    "options": question.options,
                    "correct_answer": question.correct_answer,
                    "selected_option": answer.selected_option,
                    "is_correct": answer.is_correct
                })

        # 결과 구성
        result = {
            "submission_id": submission.id,
            "quiz_id": submission.quiz_id,
            "quiz_title": quiz.title if quiz else "Unknown",
            "user_id": submission.user_id,
            "start_time": submission.start_time,
            "submit_time": submission.submit_time,
            "score": submission.score,
            "answers": answer_details
        }

        return result