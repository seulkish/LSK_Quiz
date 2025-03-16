# app/utils/cache.py
import json
from typing import Any, Optional
import redis
from functools import wraps

from app.config import settings

# Redis 클라이언트 초기화
try:
    redis_client = redis.Redis(
        host="localhost",  # settings에서 가져올 수도 있음
        port=6379,
        db=0,
        decode_responses=True
    )
    # 연결 테스트
    redis_client.ping()
    REDIS_AVAILABLE = True
except redis.exceptions.ConnectionError:
    REDIS_AVAILABLE = False
    print("Redis 서버에 연결할 수 없습니다. 캐싱이 비활성화됩니다.")

def get_cache(key: str) -> Optional[Any]:
    """Redis 캐시에서 값을 가져옵니다."""
    if not REDIS_AVAILABLE:
        return None

    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"캐시 조회 오류: {e}")
        return None

def set_cache(key: str, value: Any, expire_seconds: int = 600) -> bool:
    """Redis 캐시에 값을 저장합니다."""
    if not REDIS_AVAILABLE:
        return False

    try:
        serialized = json.dumps(value)
        redis_client.setex(key, expire_seconds, serialized)
        return True
    except Exception as e:
        print(f"캐시 저장 오류: {e}")
        return False

def delete_cache(key: str) -> bool:
    """Redis 캐시에서 키를 삭제합니다."""
    if not REDIS_AVAILABLE:
        return False

    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"캐시 삭제 오류: {e}")
        return False

def delete_pattern(pattern: str) -> bool:
    """주어진 패턴과 일치하는 모든 키를 삭제합니다."""
    if not REDIS_AVAILABLE:
        return False

    try:
        cursor = 0
        while True:
            cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                redis_client.delete(*keys)
            if cursor == 0:
                break
        return True
    except Exception as e:
        print(f"패턴 캐시 삭제 오류: {e}")
        return False

# 캐시 데코레이터 - 함수 결과를 캐싱하는 데 사용
def cached(prefix: str, expire_seconds: int = 600):
    """함수 결과를 캐싱하는 데코레이터"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not REDIS_AVAILABLE:
                return await func(*args, **kwargs)

            # 함수 이름과 인자를 기반으로 캐시 키 생성
            key = f"{prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # 캐시에서 결과 조회
            cached_result = get_cache(key)
            if cached_result is not None:
                return cached_result

            # 결과가 없으면 함수 실행
            result = await func(*args, **kwargs)

            # 결과 캐싱
            set_cache(key, result, expire_seconds)

            return result
        return wrapper
    return decorator

# 자주 사용되는 캐시 키 형식
def quiz_key(quiz_id: int) -> str:
    return f"quiz:{quiz_id}"

def questions_key(quiz_id: int) -> str:
    return f"quiz:{quiz_id}:questions"

def submission_key(submission_id: int) -> str:
    return f"submission:{submission_id}"

def user_submissions_key(user_id: int) -> str:
    return f"user:{user_id}:submissions"

def quiz_list_key(page: int, limit: int) -> str:
    return f"quiz:list:page:{page}:limit:{limit}"