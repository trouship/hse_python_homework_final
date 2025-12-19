from abc import ABC, abstractmethod

#Абстрактный класс хранилища, чтобы можно было легко заменить на БД или что-либо ещё
class AbstractStorage(ABC):
    @abstractmethod
    def save_tasks(self, tasks):
        pass

    @abstractmethod
    def restore_tasks(self):
        pass