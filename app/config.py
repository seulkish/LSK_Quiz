import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(env_path)
print(f"DATABASE_URL from env: {os.getenv('DATABASE_URL')}")

class Settings:
    PROJECT_NAME: str = "LSK Quiz"
    PROJECT_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:rlgns88@localhost:5432/lsk_quiz")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key")

    # API 설정
    API_PREFIX: str = "/api"

    # 페이징 설정
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

settings = Settings()