# app/api/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.config import settings

# OAuth2 로그인을 위한 토큰 URL 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# 현재 사용자 가져오기
def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="토큰 인증에 실패했습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 사용자입니다",
        )
    return user

# 관리자 권한 체크
def get_current_admin(
        current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다",
        )
    return current_user

# 페이징 매개변수
def get_pagination_params(
        page: int = 1,
        page_size: int = 10
) -> dict:
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10

    # 최대 페이지 크기 제한
    if page_size > 100:
        page_size = 100

    return {
        "skip": (page - 1) * page_size,
        "limit": page_size
    }