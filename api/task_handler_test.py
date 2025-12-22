import threading
import time
from functools import partial
from http.server import HTTPServer

import pytest
import requests

from api.task_handler import TaskRESTHandler
from services.task_manager import TaskManager
from storage.file_storage import FileStorage

@pytest.fixture
def task_manager(tmp_path):
    file_path = tmp_path / "test.txt"
    storage = FileStorage(file_path)
    task_manager = TaskManager(storage)
    yield task_manager

@pytest.fixture
def server(task_manager):
    task_handler = partial(TaskRESTHandler, task_manager)

    httpd = HTTPServer(("127.0.0.1", 0), task_handler)
    host, port = httpd.server_address

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    time.sleep(0.05)

    try:
        yield host, port
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=1)


def request_json(server, method, path, body=None):
    host, port = server
    url = f"http://{host}:{port}{path}"

    resp = requests.request(
        method=method,
        url=url,
        json=body,
        timeout=1.0,
    )

    payload = resp.json() if resp.content else None
    return resp.status_code, payload


def test_create_task(server):
    # Arrange
    create_body = {
        "title": "test3",
        "priority": "low"
    }

    # Act
    status, body = request_json(
        server,
        "POST",
        "/tasks",
        create_body
    )

    # Assert
    assert status == 201
    assert body["id"] == 1
    assert body["title"] == "test3"
    assert body["priority"] == "low"
    assert body["isDone"] == False

def test_create_task_invalid_priority(server):
    # Arrange
    create_body = {
        "title": "test3",
        "priority": "invalid"
    }

    # Act
    status, body = request_json(
        server,
        "POST",
        "/tasks",
        create_body
    )

    # Assert
    assert status == 400

def test_get_tasks(server):
    # Arrange
    create_body1 = {
        "title": "test3",
        "priority": "low"
    }
    create_body2 = {
        "title": "test4",
        "priority": "high"
    }
    request_json(
        server,
        "POST",
        "/tasks",
        create_body1
    )
    request_json(
        server,
        "POST",
        "/tasks",
        create_body2
    )

    # Act
    status, body = request_json(
        server,
        "GET",
        "/tasks",
    )

    # Assert
    assert status == 200
    assert len(body) == 2
    assert body[0]["id"] == 1
    assert body[0]["title"] == "test3"
    assert body[0]["priority"] == "low"
    assert body[0]["isDone"] == False
    assert body[1]["id"] == 2
    assert body[1]["title"] == "test4"
    assert body[1]["priority"] == "high"
    assert body[1]["isDone"] == False

def test_complete_task(server, task_manager):
    # Arrange
    create_body = {
        "title": "test3",
        "priority": "low"
    }
    request_json(
        server,
        "POST",
        "/tasks",
        create_body
    )

    # Act
    status, body = request_json(
        server,
        "POST",
        "/tasks/1/complete",
    )

    # Assert
    assert status == 200
    assert task_manager.tasks[0].is_done == True

def test_complete_task_not_found(server, task_manager):
    # Arrange

    # Act
    status, body = request_json(
        server,
        "POST",
        "/tasks/4/complete",
    )

    # Assert
    assert status == 404
    assert "error" in body


