# tests/test_quiz.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_and_get_quiz():
    """퀴즈 생성 및 조회 테스트"""
    # 로그인
    login_response = client.post(
        "/api/login",
        data={"username": "admin", "password": "admin1234"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 퀴즈 생성
    headers = {"Authorization": f"Bearer {token}"}
    quiz_data = {
        "title": "테스트 퀴즈",
        "description": "테스트용 퀴즈입니다.",
        "questions_count": 5,
        "randomize_questions": True,
        "randomize_options": True
    }

    response = client.post(
        f"{API_PREFIX}/quizzes",
        headers=headers,
        json=quiz_data
    )

    # 응답 확인
    assert response.status_code == 201
    quiz_id = response.json()["id"]

    # 퀴즈 조회
    get_response = client.get(
        f"/api/quizzes/{quiz_id}",
        headers=headers
    )

    assert get_response.status_code == 200
    assert get_response.json()["title"] == "테스트 퀴즈"

def test_add_question():
    """퀴즈에 문제 추가 테스트"""
    # 로그인
    login_response = client.post(
        "/api/login",
        data={"username": "admin", "password": "admin1234"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 퀴즈 생성
    quiz_data = {
        "title": "문제 추가 테스트",
        "description": "문제를 추가할 퀴즈입니다.",
        "questions_count": 3
    }

    response = client.post(
        f"{API_PREFIX}/quizzes",
        headers=headers,
        json=quiz_data
    )

    quiz_id = quiz_response.json()["id"]

    # 문제 추가
    question_data = {
        "content": "대한민국의 수도는?",
        "options": ["서울", "부산", "인천", "대전"],
        "correct_answer": 0
    }

    question_response = client.post(
        f"/api/quizzes/{quiz_id}/questions",
        headers=headers,
        json=question_data
    )

    assert question_response.status_code == 200
    assert question_response.json()["content"] == "대한민국의 수도는?"

def test_list_quizzes():
    """퀴즈 목록 조회 테스트"""
    # 로그인
    login_response = client.post(
        "/api/login",
        data={"username": "user", "password": "user1234"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 퀴즈 목록 조회
    response = client.get(
        "/api/quizzes",
        headers=headers
    )

    assert response.status_code == 200
    # 퀴즈 목록이 리스트 형태로 반환되는지 확인
    assert isinstance(response.json(), list)