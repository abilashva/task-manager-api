import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("TASKS_DB", str(tmp_path / "test.db"))
    with TestClient(app) as c:  # runs lifespan -> creates tables
        yield c


def make(client, **overrides):
    body = {"title": "Write report", "priority": "high"}
    body.update(overrides)
    return client.post("/tasks", json=body)


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_get(client):
    r = make(client, due_date="2026-12-01")
    assert r.status_code == 201
    task = r.json()
    assert task["id"] == 1 and task["status"] == "todo" and task["due_date"] == "2026-12-01"
    assert client.get("/tasks/1").json()["title"] == "Write report"


def test_validation_rejects_bad_input(client):
    assert make(client, title="").status_code == 422
    assert make(client, priority="urgent").status_code == 422


def test_list_filters(client):
    make(client, title="Alpha", priority="low")
    make(client, title="Beta", priority="high", status="done")
    make(client, title="Gamma", priority="high")
    assert len(client.get("/tasks").json()) == 3
    assert len(client.get("/tasks", params={"priority": "high"}).json()) == 2
    assert [t["title"] for t in client.get("/tasks", params={"status": "done"}).json()] == ["Beta"]
    assert [t["title"] for t in client.get("/tasks", params={"search": "gam"}).json()] == ["Gamma"]
    assert len(client.get("/tasks", params={"limit": 1}).json()) == 1


def test_partial_update(client):
    make(client)
    r = client.patch("/tasks/1", json={"status": "in_progress"})
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress" and r.json()["title"] == "Write report"
    assert client.patch("/tasks/1", json={}).status_code == 400


def test_delete(client):
    make(client)
    assert client.delete("/tasks/1").status_code == 204
    assert client.get("/tasks/1").status_code == 404
    assert client.delete("/tasks/1").status_code == 404


def test_missing_task_404(client):
    assert client.get("/tasks/999").status_code == 404
    assert client.patch("/tasks/999", json={"title": "x"}).status_code == 404
