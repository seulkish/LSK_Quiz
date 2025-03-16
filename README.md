# LSK Quiz - 퀴즈 응시 시스템 API 프로젝트
FastAPI와 PostgreSQL을 사용하여 구현한 퀴즈 응시 시스템 API 과제입니다.

## 구현된 API 엔드포인트

### 1. 퀴즈 생성/수정/삭제 API (관리자용)

- `GET /api/quizzes/` - 퀴즈 목록 조회
- `POST /api/quizzes/` - 퀴즈 생성
- `GET /api/quizzes/{quiz_id}` - 퀴즈 상세 조회
- `PUT /api/quizzes/{quiz_id}` - 퀴즈 수정
- `DELETE /api/quizzes/{quiz_id}` - 퀴즈 삭제
- `POST /api/quizzes/{quiz_id}/questions` - 문제 추가

#### 주요 기능:
- 퀴즈 생성 및 관리 기능 (관리자만 가능)
- 여러 문제를 포함한 퀴즈 관리
- n+2지선다 문제 형식

### 2. 퀴즈 조회/응시 API

- `GET /api/quizzes/` - 퀴즈 목록 조회 (페이징 처리)
- `GET /api/quizzes/{quiz_id}` - 퀴즈 상세 조회
- `GET /api/quizzes/{quiz_id}/take` - 퀴즈 응시 (랜덤 문제 출제)

#### 주요 기능:
- 관리자/사용자 권한별 퀴즈 목록 조회
- 페이징 처리된 문제 조회
- 랜덤 문제 출제
- 문제/선택지 랜덤 배치

### 3. 응시 및 답안 제출 API

- `GET /api/submissions/my` - 내 제출 목록 조회
- `GET /api/submissions/{submission_id}` - 제출 상세 조회
- `POST /api/submissions/{submission_id}/save` - 진행 상황 저장
- `POST /api/submissions/{submission_id}/answers` - 답안 제출 및 자동 채점

#### 주요 기능:
- 새로고침 시 상태 유지
- 제출 자동 채점

## 프로젝트 구조

```
LSK_Quiz/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── quiz.py
│   │   ├── submission.py
│   │   ├── user.py
│   │   └── deps.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── quiz.py
│   │   ├── question.py
│   │   └── submission.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── quiz.py
│   │   ├── user.py
│   │   └── submission.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── quiz.py
│   │   └── submission.py
│   └── utils/
│       ├── __init__.py
│       ├── auth.py
│       └── cache.py
├── tests/
│   ├── test_quiz.py
│   └── test_submission.py
├── migrations/
├── .env
├── alembic.ini
├── pyproject.toml
├── generate_key.py
├── debug_tables.py
└── setup_db.py
```

## 참고사항
- setup_db.py: 초기 테이블과 테스트 계정(admin/admin1234, user/user1234) 생성 파일 
- generate_key.py: JWT 토큰용 시크릿 키 생성 유틸리티
- debug_tables.py: DB 연결 테스트 파일 

## 요구사항 구현 내용

1. 퀴즈 생성/수정/삭제 API
    - 관리자 권한 구분
    - 여러 문제 포함 가능
    - N+2지선다 구현

2. 퀴즈 조회/응시 API
    - 페이징 처리
    - 랜덤 문제 출제
    - 문제/선택지 랜덤 배치

3. 응시 및 답안 제출 API
    - 새로고침 대응
    - 자동 채점

4. 기타 요구사항
    - API 문서화
    - Redis 캐싱 구현