from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
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
            raise TypeError(f"priorty param must be a priority enum, but got {type(priority)}")
        
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
        if not self._file_path.exists():
            print(f"restore file not found {self._file_path}")
            return []

        tasks = []

        with self._file_path.open('r', encoding="utf-8") as r:
            for line in r:
                try:
                    data_task = json.loads(line)
                    task = Task.from_dict(data_task)
                    tasks.append(task)
                except Exception as e:
                    print(f"restore parse error: {e} {line}")
                    
        return tasks

class TaskManager:
    def __init__(self, storage):
        self._tasks = []
        self._next_task_id = 1
        self._storage = storage

    def add_task(self, title, priority):
        task = Task(title, priority, False, self._next_task_id)
        self._tasks.append(task)
        self._next_task_id += 1
        return task

    @property
    def tasks(self):
        return self._tasks

    def save_tasks(self):
        self._storage.save_tasks(self._tasks)

    def restore_tasks(self):
        self._tasks = self._storage.restore_tasks()

    def complete_task(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                task.complete()

class TaskRESTHandler(BaseHTTPRequestHandler):
    def _read_json_body(self):
        length = int(self.headers.get('content-length', 0))
        raw = self.rfile.read(length) if length > 0 else b""
        if not raw:
            return None
        try:
            return json.loads(raw)
        except Exception as e:
            print(f"read body error: {e} {raw}")
            return None

    def _send_json(self, data, status=200):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _error(self, status, msg):
        self._send_json({"error": msg, "status": status})

    def create_task(self):
        pass

    def complete_task(self, task_id):
        pass

    def get_tasks(self):
        pass

    def do_POST(self):
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]

        if parsed.path == "/tasks":
            self.create_task()
        elif len(parts) == 3 and parts[0] == "tasks" and parts[2] == "complete":
            self.complete_task(parts[1])
        else:
            self._error(400, "Not found")

    def do_GET(self):
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]

        if parsed.path == "/tasks":
            self.get_tasks()
        else:
            self._error(400, "Not found")


