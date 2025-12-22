from storage.abstract_storage import AbstractStorage
from pathlib import Path
from models.task import Task
import json


# Класс файлового хранилища
class FileStorage(AbstractStorage):
    def __init__(self, file_path):
        self._file_path = Path(file_path)

    def save_tasks(self, tasks):
        # Записываем записи формата json в файла
        with self._file_path.open('w', encoding="utf-8") as f_write:
            for task in tasks:
                try:
                    json_task = json.dumps(task.to_dict())
                    f_write.write(json_task + '\n')
                except Exception as e:
                    print(f"save parse error: {e} {task}")

    def restore_tasks(self):
        # Проверка существования файла
        if not self._file_path.exists():
            print(f"restore file not found {self._file_path}")
            return []

        tasks = []

        # Считываем записи формата json из файла
        with self._file_path.open('r', encoding="utf-8") as f_read:
            for line in f_read:
                line = line.strip()
                if not line:
                    continue

                try:
                    data_task = json.loads(line)
                    task = Task.from_dict(data_task)
                    tasks.append(task)
                except Exception as e:
                    print(f"restore parse error: {e} {line}")

        return tasks
