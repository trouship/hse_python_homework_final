from models.priority import Priority
from models.task import Task
from storage.abstract_storage import AbstractStorage

#Класс для управления список задач
class TaskManager:
    def __init__(self, storage):
        #Проверка на тип хранилища
        if not isinstance(storage, AbstractStorage):
            raise TypeError("storage must be an instance of AbstractStorage")

        self._tasks = []
        self._next_task_id = 1
        self._storage = storage

    #Добавление задачи в список
    def add_task(self, title, priority):
        if not title or not isinstance(title, str):
            raise ValueError("Title must be a non-empty string")
        if not isinstance(priority, Priority):
            raise TypeError("Priority must be a Priority enum")

        task = Task(title, priority, False, self._next_task_id)
        self._tasks.append(task)
        self._next_task_id += 1
        return task

    @property
    def tasks(self):
        #Возвращаем копию, чтобы не могли поменять наш список
        return self._tasks.copy()

    def save_tasks(self):
        self._storage.save_tasks(self._tasks)

    def restore_tasks(self):
        self._tasks = self._storage.restore_tasks()
        if self._tasks:
            #Присваиваем максимальный id + 1 для уникальности
            self._next_task_id = max(task.id for task in self._tasks) + 1

    def complete_task(self, task_id):
        #Поиск задачи, если нашли и выполнили, то True, иначе False
        for task in self._tasks:
            if task.id == task_id:
                task.complete()
                return True

        return False
