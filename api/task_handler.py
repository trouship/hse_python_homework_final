import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from models.priority import Priority

#Класс обработчик запросов
class TaskRESTHandler(BaseHTTPRequestHandler):
    def __init__(self, task_manager, *args, **kwargs):
        #Добавляем объект для управления списком задач
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
        self._send_json({"error": msg}, status)

    def create_task(self):
        body = self._read_json_body()
        if not body or "title" not in body or "priority" not in body:
            self._error(400, "Title and Priority must be specified")
            return

        #Проверка на соответствие приоритета элементу из заданного Enum
        try:
            priority = Priority[body["priority"]]
        except Exception as e:
            print(f"create task error: priority must be 'low', 'medium' or 'high', but got {body["priority"]}")
            self._error(400, f"create task error: priority must be 'low', 'medium' or 'high', but got '{body["priority"]}'")
            return

        #Добавляем задачу и сохраняем файл
        task = self._task_manager.add_task(body["title"], priority)
        self._task_manager.save_tasks()
        #Отправляем в ответ созданную задачу
        self._send_json(task.to_dict(), 201)

    def complete_task(self, task_oid):
        #Проверка на тип id
        try:
            task_id = int(task_oid)
        except Exception as e:
            print(f"complete task error: {e} {task_oid}")
            self._error(400, "Task id must be integer")
            return

        #Если не нашли задачу, то возвращаем 404
        if not self._task_manager.complete_task(task_id):
            self._error(404, "Task not found")
        else:
            #Иначе пустое тело ответа и сохраняем задачи
            self._send_json({}, 200)
            self._task_manager.save_tasks()

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
            self._error(404, "Not found")

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/tasks":
            self.get_tasks()
        else:
            self._error(404, "Not found")