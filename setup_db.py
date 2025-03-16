# setup_db.py
from app.db import Base, engine
from app.models.user import User
from app.utils.auth import get_password_hash
from sqlalchemy.orm import sessionmaker

# 모델 임포트
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.submission import Submission, SubmissionAnswer

# 테이블 생성
Base.metadata.create_all(bind=engine)
print("데이터베이스 테이블 생성 완료")

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# 테스트용 계정 생성
admin = User(
    username="admin",
    email="admin@example.com",
    hashed_password=get_password_hash("admin1234"),
    is_active=True,
    is_admin=True
)

user = User(
    username="user",
    email="user@example.com",
    hashed_password=get_password_hash("user1234"),
    is_active=True,
    is_admin=False
)

# 사용자 추가
db.add(admin)
db.add(user)
db.commit()

print("테스트 사용자 생성 완료")
db.close()