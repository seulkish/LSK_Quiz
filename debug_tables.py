# debug_tables.py
import logging
from sqlalchemy import text
from app.db import Base, engine
from app.models.user import User
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.submission import Submission, SubmissionAnswer

# 로깅 설정
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 데이터베이스 연결 테스트
print("데이터베이스 연결 테스트 중...")
conn = engine.connect()
result = conn.execute(text("SELECT current_database();"))
db_name = result.scalar()
print(f"연결된 데이터베이스: {db_name}")
conn.close()

# 테이블 생성 시도
print("테이블 생성 시도 중...")
try:
    Base.metadata.create_all(bind=engine)
    print("테이블 생성 완료")
except Exception as e:
    print(f"테이블 생성 중 오류 발생: {e}")