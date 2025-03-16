# tests/test_submission.py
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

# API 접두사 가져오기
API_PREFIX = settings.API_PREFIX
client = TestClient(app)

def test_submit_answer():
    """답안 제출 테스트"""
    # 로그인
    login_response = client.post(
        f"{API_PREFIX}/users/login",
        data={"username": "admin", "password": "admin1234"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 퀴즈 조회
    quizzes_response = client.get(
        f"{API_PREFIX}/quizzes",
        headers=headers
    )

    assert quizzes_response.status_code == 200

    # 응답 체크
    quizzes = quizzes_response.json()
    if not quizzes or len(quizzes) == 0:
        print("테스트할 퀴즈가 없습니다.")
        return

    quiz_id = quizzes[0]["id"]

    # 퀴즈 응시 시작 (문제 조회)
    take_response = client.get(
        f"{API_PREFIX}/quizzes/{quiz_id}/take",
        headers=headers
    )

    assert take_response.status_code == 200
    questions = take_response.json()

    # 제출 ID 확인
    submissions_response = client.get(
        f"{API_PREFIX}/submissions/my",
        headers=headers
    )

    submissions = submissions_response.json()
    submission_id = None

    for submission in submissions:
        if submission["quiz_id"] == quiz_id and not submission["is_completed"]:
            submission_id = submission["id"]
            break

    if not submission_id:
        print("진행 중인 제출을 찾을 수 없습니다.")
        return

    # 답안 작성
    answers = []
    for question in questions:
        answers.append({
            "question_id": question["id"],
            "selected_option": 0  # 모든 문제에 첫 번째 선택지를 선택
        })

    # 답안 제출
    submit_response = client.post(
        f"{API_PREFIX}/submissions/{submission_id}/answers",
        headers=headers,
        json=answers
    )

    assert submit_response.status_code == 201
    assert "score" in submit_response.json()

def test_save_progress():
    """답안 중간 저장 테스트"""
    # 로그인
    login_response = client.post(
        f"{API_PREFIX}/users/login",
        data={"username": "admin", "password": "admin1234"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 퀴즈 조회
    quizzes_response = client.get(
        f"{API_PREFIX}/quizzes",
        headers=headers
    )

    quizzes = quizzes_response.json()
    if not quizzes or len(quizzes) == 0:
        print("테스트할 퀴즈가 없습니다.")
        return

    quiz_id = quizzes[0]["id"]

    # 퀴즈 응시 시작
    take_response = client.get(
        f"{API_PREFIX}/quizzes/{quiz_id}/take",
        headers=headers
    )

    questions = take_response.json()

    # 제출 ID 확인
    submissions_response = client.get(
        f"{API_PREFIX}/submissions/my",
        headers=headers
    )

    submissions = submissions_response.json()
    submission_id = None

    for submission in submissions:
        if submission["quiz_id"] == quiz_id and not submission["is_completed"]:
            submission_id = submission["id"]
            break

    if not submission_id:
        print("진행 중인 제출을 찾을 수 없습니다.")
        return

    # 일부 답안만 저장
    partial_answers = []
    for question in questions[:2]:  # 처음 2개 문제만 답변
        partial_answers.append({
            "question_id": question["id"],
            "selected_option": 1  # 두 번째 선택지 선택
        })

    # 진행 상태 저장
    save_response = client.post(
        f"{API_PREFIX}/submissions/{submission_id}/save",
        headers=headers,
        json=partial_answers
    )

    assert save_response.status_code == 200
    assert "message" in save_response.json()

def test_view_submission_results():
    """제출 결과 조회 테스트"""
    # 로그인
    login_response = client.post(
        f"{API_PREFIX}/users/login",
        data={"username": "admin", "password": "admin1234"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 제출 목록 조회
    submissions_response = client.get(
        f"{API_PREFIX}/submissions/my",
        headers=headers
    )

    # 응답 확인
    assert submissions_response.status_code == 200
    submissions = submissions_response.json()

    # 리스트가 비어있는지 확인
    if not submissions or len(submissions) == 0:
        print("제출 기록이 없습니다.")
        return

    # 완료된 제출 찾기
    completed_submissions = [s for s in submissions if s["is_completed"]]

    if not completed_submissions:
        print("완료된 제출이 없습니다.")
        return

    # 첫 번째 완료된 제출 결과 조회
    submission_id = completed_submissions[0]["id"]

    result_response = client.get(
        f"{API_PREFIX}/submissions/{submission_id}",
        headers=headers
    )

    assert result_response.status_code == 200
    result = result_response.json()

    assert "score" in result
    assert result["is_completed"] == True