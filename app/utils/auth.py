# app/utils/auth.py
from passlib.context import CryptContext

# bcrypt 사용
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 비밀번호 검증
def verify_password(plain_password, hashed_password):
    # 입력받은 비밀번호와 해시된 비밀번호 비교
    return pwd_context.verify(plain_password, hashed_password)

# 비밀번호 해싱
def get_password_hash(password):
    # 비밀번호 해싱해서 반환
    return pwd_context.hash(password)