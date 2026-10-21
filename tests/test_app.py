import pytest

from app import app, tasks


@pytest.fixture
def client():
    """Provide a Flask test client with isolated task data."""
    original_tasks = list(tasks)
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Existing task"},
    ])

    with app.test_client() as test_client:
        yield test_client

    tasks.clear()
    tasks.extend(original_tasks)


def test_existing_tasks_default_to_medium(client):
    """Tasks without stored priorities are returned as Medium."""
    response = client.get("/api/tasks")

    assert response.status_code == 200
    assert response.get_json() == [{
        "id": 1,
        "title": "Existing task",
        "priority": "Medium",
    }]


def test_create_task_defaults_to_medium(client):
    """Creating a task without priority defaults to Medium."""
    response = client.post(
        "/api/tasks",
        json={"title": "New task"},
    )

    assert response.status_code == 201
    assert response.get_json()["priority"] == "Medium"
    assert tasks[-1]["priority"] == "Medium"


def test_create_task_persists_valid_priority(client):
    """Creating a task stores and returns a valid priority."""
    response = client.post(
        "/api/tasks",
        json={"title": "Urgent task", "priority": "High"},
    )

    assert response.status_code == 201
    assert response.get_json()["priority"] == "High"
    assert tasks[-1]["priority"] == "High"


def test_create_task_rejects_invalid_priority(client):
    """Creating a task rejects values outside the supported priorities."""
    response = client.post(
        "/api/tasks",
        json={"title": "Invalid task", "priority": "Critical"},
    )

    assert response.status_code == 400
    assert "Priority" in response.get_json()["error"]


def test_update_task_changes_priority(client):
    """Updating a task persists the requested priority."""
    response = client.put(
        "/api/tasks/1",
        json={"priority": "Low"},
    )

    assert response.status_code == 200
    assert response.get_json()["priority"] == "Low"
    assert tasks[0]["priority"] == "Low"


def test_update_task_defaults_omitted_priority_to_medium(client):
    """Updating without priority resets the priority to Medium."""
    tasks[0]["priority"] = "High"

    response = client.put(
        "/api/tasks/1",
        json={"title": "Renamed task"},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "id": 1,
        "title": "Renamed task",
        "priority": "Medium",
    }
    assert tasks[0]["priority"] == "Medium"


def test_update_task_rejects_invalid_priority(client):
    """Updating a task rejects invalid priority values."""
    response = client.put(
        "/api/tasks/1",
        json={"priority": "Critical"},
    )

    assert response.status_code == 400
    assert tasks[0].get("priority") is None
