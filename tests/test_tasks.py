from app.models import TaskPriority, TaskStatus


def test_create_task_valid_returns_201_with_full_body(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Write tests",
            "description": "Cover module 2 endpoints",
            "status": "InProgress",
            "priority": "High",
            "assignee": "Ada",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Write tests"
    assert body["description"] == "Cover module 2 endpoints"
    assert body["status"] == TaskStatus.IN_PROGRESS.value
    assert body["priority"] == TaskPriority.HIGH.value
    assert body["assignee"] == "Ada"
    assert body["id"]
    assert body["created_at"]
    assert body["updated_at"]


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={})

    assert response.status_code == 422


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})

    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    response = client.post("/tasks", json={"title": "Bad priority", "priority": "Urgent"})

    assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    response = client.post("/tasks", json={"title": "Bad payload", "unexpected": True})

    assert response.status_code == 422


def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client):
    client.post("/tasks", json={"title": "One task", "status": "ToDo"})

    response = client.get("/tasks", params={"status": TaskStatus.DONE.value})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "Low task", "priority": TaskPriority.LOW.value})
    client.post("/tasks", json={"title": "High task", "priority": TaskPriority.HIGH.value})

    response = client.get("/tasks", params={"priority": TaskPriority.HIGH.value})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "High task"
    assert body[0]["priority"] == TaskPriority.HIGH.value


def test_get_task_by_id_returns_task(client, created_task):
    response = client.get(f"/tasks/{created_task['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created_task["id"]
    assert body["title"] == created_task["title"]


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    response = client.get("/tasks/missing-id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task with id missing-id not found"}


def test_patch_partial_update_keeps_other_fields(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"title": "Updated title"})

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Updated title"
    assert body["description"] == ""
    assert body["status"] == TaskStatus.TODO.value
    assert body["priority"] == TaskPriority.MEDIUM.value
    assert body["assignee"] is None


def test_patch_not_found_returns_404(client):
    response = client.patch("/tasks/missing-id", json={"title": "Nope"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Task with id missing-id not found"}


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": TaskStatus.IN_PROGRESS.value})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == TaskStatus.IN_PROGRESS.value


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": TaskStatus.DONE.value})

    assert response.status_code == 422


def test_patch_same_status_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": TaskStatus.TODO.value})

    assert response.status_code == 422


def test_delete_existing_returns_204_no_body(client, created_task):
    response = client.delete(f"/tasks/{created_task['id']}")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client):
    response = client.delete("/tasks/missing-id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task with id missing-id not found"}

def test_patch_invalid_status_value_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "Queued"})

    assert response.status_code == 422
    assert response.json()["detail"]

def test_patch_empty_json_body_returns_200_no_changes(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={})

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == created_task["title"]
    assert body["status"] == created_task["status"]