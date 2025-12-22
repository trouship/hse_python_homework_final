import pytest
import json

from storage.file_storage import FileStorage
import models


def test_file_storage_save_task_count_is_valid(tmp_path):
    # Arrange
    file_path = tmp_path / 'test.txt'
    storage = FileStorage(file_path)
    task1 = models.task.Task("test1", models.priority.Priority.low, True, 1)
    task2 = models.task.Task("test2", models.priority.Priority.high, False, 2)
    tasks = [task1, task2]

    # Act
    storage.save_tasks(tasks)

    line_count = 0
    with open(file_path, 'r', encoding='utf-8') as f_read:
        for line in f_read:
            line_count += 1

    # Assert
    assert line_count == 2


def test_file_storage_save_task_is_valid(tmp_path):
    # Arrange
    file_path = tmp_path / 'test.txt'
    storage = FileStorage(file_path)
    task1 = models.task.Task("test1", models.priority.Priority.low, True, 1)
    tasks = [task1]

    # Act
    storage.save_tasks(tasks)

    line_count = 0
    with open(file_path, 'r', encoding='utf-8') as f_read:
        task = json.load(f_read)

    # Assert
    assert task['title'] == 'test1'
    assert task['priority'] == 'low'
    assert task['isDone'] == True
    assert task['id'] == 1


def test_file_storage_restore_task_is_valid(tmp_path):
    # Arrange
    file_path = tmp_path / 'test.txt'
    storage = FileStorage(file_path)
    task_dict = {
        'title': 'test1',
        'priority': 'low',
        'isDone': False,
        'id': 1,
    }

    # Act
    # Записываем в файл
    with open(file_path, 'w', encoding='utf-8') as f_write:
        f_write.write(json.dumps(task_dict))
    # Читаем
    tasks = storage.restore_tasks()

    # Assert
    assert len(tasks) == 1
    assert tasks[0].title == 'test1'
    assert tasks[0].priority == 'low'
    assert tasks[0].is_done == False
    assert tasks[0].id == 1
