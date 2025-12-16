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
        self.__title = title
        self.__priority = priority
        self.__is_done = is_done
        self.__id = id

    @property
    def title(self):
        return self.__title

    @property
    def id(self):
        return self.__id

    @property
    def is_done(self):
        return self.__id_done

    @property
    def id(self):
        return self.__id

    def complete(self):
        __is_done = true

class FileStorage:
    def __init__(self, file_path):
        self.__file_path = Path(file_path)

    def save_tasks(self, tasks):
        with self.__file_path.open('w', encoding="utf-8") as w:
            for task in tasks:
                try:
                    json_task = json.dumps(task)
                except:
                    print(f"Save parse error: {task}")
                    continue;

                w.write(json_task + '\n')                
                

    def restore_tasks(self, tasks):
        if not self.__file_path.exists():
            raise FileNotFoundError

        with self.__file_path.open('r', encoding="utf-8") as r:
            for line in r:
                try:
                    task = json.loads(line)
                except:
                    print(f"Restore parse error: {line}")
                    continue;

                append(tasks, task)


            
        
