import pytest
from models.priority import Priority
from models.task import Task

def test_task_to_dict_is_valid():
    # Arrange
    title = "test"
    test_priority = Priority.high
    is_done = True
    test_id = 1
    test_task = Task(title, test_priority, is_done, test_id)

    # Act
    dict = test_task.to_dict()

    # Assert
    assert dict['title'] == title
    assert dict['priority'] == test_priority.name
    assert dict['isDone'] == is_done
    assert dict['id'] == test_id

def test_task_from_dict_is_valid():
    # Arrange
    title = "test_from_dict"
    test_priority = Priority.medium
    is_done = False
    test_id = 2
    dict = {
        'title': title,
        'priority': test_priority.name,
        'isDone': is_done,
        'id': test_id
    }

    # Act
    task = Task.from_dict(dict)

    # Assert
    assert task.title == title
    assert task.priority == test_priority.name
    assert task.is_done == is_done
    assert task.id == test_id
