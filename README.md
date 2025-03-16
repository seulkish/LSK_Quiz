# LSK Quiz - 퀴즈 응시 시스템 API 프로젝트
FastAPI와 PostgreSQL을 사용하여 구현한 퀴즈 응시 시스템 API 과제입니다.

## 실행 방법

### 필수 사항
- Python 3.11 이상
- PostgreSQL 서버
- Redis 서버 (캐싱 기능 사용 시)

### 설치 및 환경 설정

1. 저장소 클론
```bash
git clone https://github.com/seulkish/LSK_Quiz.git
cd LSK_Quiz
```

2. 의존성 설치
```bash
# Poetry 설치
pip install poetry

# 프로젝트 의존성 설치
# (pyproject.toml 파일에 정의된 모든 의존성을 한 번에 설치합니다)
poetry install
```

** 참고: 현 프로젝트에 새 패키지를 추가하려면 아래 명령어를 사용합니다
```bash
poetry add [패키지명]
```

3. 보안 키 생성
```bash
python generate_key.py
```
위 명령어를 실행하면 시크릿 키가 생성됩니다. 이 값을 다음 단계에서 사용하세요.

4. 환경변수 설정
   `.env` 파일을 프로젝트 루트 디렉토리에 생성하고 아래 내용을 입력하세요.
   PostgreSQL 접속 정보와 위에서 생성한 시크릿 키를 환경에 맞게 수정하세요.
```
# 데이터베이스 연결 정보
DATABASE_URL=postgresql://사용자명:비밀번호@localhost:5432/lsk_quiz

# 보안 설정 - generate_key.py 실행하여 얻은 값을 넣으세요
SECRET_KEY=실행결과값을여기에붙여넣기

# 기타 환경 설정
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. 데이터베이스 생성
   PostgreSQL에서 먼저 데이터베이스를 생성해야 합니다.
```sql
CREATE DATABASE lsk_quiz;
```
또는 PostgreSQL GUI 도구를 사용하여 데이터베이스를 생성할 수도 있습니다.

6. 데이터베이스 초기화 및 테스트 데이터 생성
```bash
python setup_db.py
```

7. 마이그레이션 실행
```bash
alembic upgrade head
```

### 서버 실행

```bash
# Poetry를 사용하는 경우
poetry run uvicorn app.main:app --reload

# 또는 직접 실행하는 경우
uvicorn app.main:app --reload
```

서버가 실행되면 다음 URL로 접속할 수 있습니다:
- API 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs

### 테스트 계정

초기 설정 후 생성되는 테스트 계정:
- 관리자: username=`admin`, password=`admin1234`
- 일반사용자: username=`user`, password=`user1234`

### 테스트 실행

```bash
# Poetry를 사용하는 경우
poetry run pytest tests/

# 또는 직접 실행하는 경우
pytest tests/
```

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