from enum import Enum
from pathlib import Path
import json

TASKS = []
NEXT_TASK_ID = 1
FILE_PATH = "tasks.txt"

class Priority(Enum):
    low = 1
    medium = 2
    high = 3

class Task:
    def __init__(self, title, priority, is_done, id):
        if type(priority) is not Priority:
            raise TypeError(f"priorty param must be a priority enum, but got {type(priority))}")
        
        self._title = title
        self._priority = priority
        self._is_done = is_done
        self._id = id

    @property
    def title(self):
        return self._title

    @property
    def priority(self):
        return self._priority.name

    @property
    def is_done(self):
        return self._is_done

    @property
    def id(self):
        return self._id

    def complete(self):
        self._is_done = True

    def to_dict(self):
        return {
            "title": self._title,
            "priority": self._priority.value,
            "is_done": self._is_done,
            "id": self._id,
        }

    @staticmethod
    def from_dict(data):
        return Task(data["title"],
                    Priority(data["priority"]),
                    data["is_done"],
                    data["id"]
        )

class FileStorage:
    def __init__(self, file_path):
        self._file_path = Path(file_path)

    def save_tasks(self, tasks):
        with self._file_path.open('w', encoding="utf-8") as w:
            for task in tasks:
                try:
                    json_task = json.dumps(task.to_dict())
                    w.write(json_task + '\n')
                except Exception as e:
                    print(f"save parse error: {e} {task}")

    def restore_tasks(self):
        if not self.__file_path.exists():
            print($"restore file not found {self._file_path}")
            return []

        tasks = []

        with self.__file_path.open('r', encoding="utf-8") as r:
            for line in r:
                try:
                    data_task = json.loads(line)
                    task = Task.from_dict(data_task)
                    tasks.append(task)
                except Exception as e:
                    print(f"restore parse error: {e} {line}")
                    
        return tasks
