from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from enum import Enum
from pathlib import Path
from functools import partial
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
                return True

        return False

class TaskRESTHandler(BaseHTTPRequestHandler):
    def __init__(self, task_manager, *args, **kwargs):
        self._task_manager = task_manager
        super().__init__(*args, **kwargs)

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
        body = self._read_json_body()
        if not body or "title" not in body or "priority" not in body:
            self._error(400, "Title or Priority must be specified")
            return

        try:
            priority = Priority(body["priority"])
            task = self._task_manager.add_task(body["title"], priority)
            self._task_manager.save_tasks()
            self._send_json(task.to_dict(), 201)
        except Exception as e:
            print(f"create task error: {e} {body}")
            self._error(400, f"create task error: {e}")

    def complete_task(self, task_id):
        try:
            if not self._task_manager.complete_task(int(task_id)):
                self._error(404, "Task not found")
            else:
                self._send_json({}, 200)
                self._task_manager.save_tasks()
        except Exception as e:
            self._error(500, "complete task error")
            print(f"complete task error: {e} {task_id}")

    def get_tasks(self):
        tasks = [task.to_dict() for task in self._task_manager.tasks]
        self._send_json(tasks, 200)

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

def run(host="127.0.0.1", port=8000):
    storage = FileStorage(FILE_PATH)
    task_manager = TaskManager(storage)

    task_manager.restore_tasks()

    handler = partial(TaskRESTHandler, task_manager)

    print(f"Serving on http://{host}:{port}")
    server = HTTPServer((host, port), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
        server.server_close()

if __name__ == "__main__":
    run()