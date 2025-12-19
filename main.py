from functools import partial
from http.server import HTTPServer

from api.task_handler import TaskRESTHandler
from services.task_manager import TaskManager
from storage.file_storage import FileStorage

#Константа для пути к файлу с задачами, по заданию именно .txt
FILE_PATH = "tasks.txt"

def run(host="127.0.0.1", port=8000):
    #Создаем хранилище и менеджер задач
    storage = FileStorage(FILE_PATH)
    task_manager = TaskManager(storage)

    #Получаем ранее созданные задачи
    task_manager.restore_tasks()

    #Добавлем менеджер задач к обработчику
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
