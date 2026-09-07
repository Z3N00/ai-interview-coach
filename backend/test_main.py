from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AI Interview Coach API running!"}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_topics():
    response = client.get("/topics")
    assert response.status_code == 200
    assert "topics" in response.json()
    assert len(response.json()["topics"]) == 5

def test_start_interview_missing_fields():
    response = client.post("/start-interview", json={})
    assert response.status_code == 422

def test_start_interview_invalid_topic():
    response = client.post("/start-interview", json={
        "candidate_name": "Kartik",
        "topic": ""
    })
    assert response.status_code == 422

def test_submit_answer_invalid_session():
    response = client.post("/submit-answer", json={
        "session_id": "invalid-session-id",
        "answer": "test answer"
    })
    assert response.status_code == 404