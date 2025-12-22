import pytest

from models.priority import Priority
from models.task import Task
from services.task_manager import TaskManager
from storage.file_storage import FileStorage


def test_task_manager_add_task_is_valid(tmp_path):
    # Arrange
    file_path = tmp_path / "test.txt"
    storage = FileStorage(file_path)
    task_manager = TaskManager(storage)

    # Act
    task_manager.add_task("test1", Priority.high)

    # Assert
    assert len(task_manager.tasks) == 1
    task = task_manager.tasks[0]
    assert isinstance(task, Task)
    assert task.title == "test1"
    assert task.priority == Priority.high.name
    assert task.is_done == False
    assert task.id == 1

def test_task_manager_complete_task_is_valid(tmp_path):
    # Arrange
    file_path = tmp_path / "test.txt"
    storage = FileStorage(file_path)
    task_manager = TaskManager(storage)
    task_manager.add_task("test1", Priority.low)

    # Act
    task_manager.complete_task(1)

    # Assert
    assert task_manager.tasks[0].is_done == True



