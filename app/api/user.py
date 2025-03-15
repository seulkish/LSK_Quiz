# app/api/user.py
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt

from app.api.deps import get_current_user, get_current_admin
from app.db import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema
from app.utils.auth import get_password_hash, verify_password
from app.config import settings

router = APIRouter()

# 사용자 목록 조회 (관리자만)
@router.get("/", response_model=List[UserSchema])
def read_users(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_admin),
) -> Any:
    """사용자 목록 조회 (관리자 전용)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# 현재 사용자 정보 조회
@router.get("/me", response_model=UserSchema)
def read_user_me(
        current_user: User = Depends(get_current_user),
) -> Any:
    """현재 로그인한 사용자 정보 조회"""
    return current_user

# 특정 사용자 정보 조회
@router.get("/{user_id}", response_model=UserSchema)
def read_user(
        user_id: int,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db),
) -> Any:
    """특정 사용자 정보 조회 (관리자 전용)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    return user

# 사용자 생성
@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(
        *,
        db: Session = Depends(get_db),
        user_in: UserCreate,
) -> Any:
    """새 사용자 등록"""
    # 사용자명 중복 체크
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 사용자명입니다"
        )

    # 이메일 중복 체크
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다"
        )

    # 비밀번호 해싱
    hashed_password = get_password_hash(user_in.password)

    # 새 사용자 생성
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=False  # 기본적으로 관리자 권한 없음
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# 로그인 및 토큰 발급
@router.post("/login")
def login_for_access_token(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """사용자 로그인 및 액세스 토큰 발급"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 사용자명 또는 비밀번호입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 토큰 만료 시간 설정 (예: 30일)
    access_token_expires = timedelta(days=30)

    # JWT 토큰 생성
    data = {
        "sub": str(user.id),
        "exp": datetime.utcnow() + access_token_expires
    }
    access_token = jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")

    return {"access_token": access_token, "token_type": "bearer"}

# 사용자 업데이트 (본인만)
@router.put("/me", response_model=UserSchema)
def update_user_me(
        *,
        db: Session = Depends(get_db),
        user_in: UserUpdate,
        current_user: User = Depends(get_current_user),
) -> Any:
    """현재 사용자 정보 업데이트"""
    # 이메일 중복 체크
    if user_in.email and user_in.email != current_user.email:
        user = db.query(User).filter(User.email == user_in.email).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 이메일입니다"
            )

    # 사용자 정보 업데이트
    update_data = user_in.dict(exclude_unset=True)

    # 비밀번호가 있으면 해싱
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

# 특정 사용자 업데이트 (관리자만)
@router.put("/{user_id}", response_model=UserSchema)
def update_user(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        user_in: UserUpdate,
        current_user: User = Depends(get_current_admin),
) -> Any:
    """특정 사용자 정보 업데이트 (관리자 전용)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    # 사용자 정보 업데이트
    update_data = user_in.dict(exclude_unset=True)

    # 비밀번호가 있으면 해싱
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]

    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user