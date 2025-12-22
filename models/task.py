from models.priority import Priority


#Класс задания
class Task:
    def __init__(self, title, priority, is_done, id):
        #Проверка на тип приоритета
        if not isinstance(priority, Priority):
            raise TypeError(f"priority param must be a priority enum, but got {type(priority)}")

        self._title = title
        self._priority = priority
        self._is_done = is_done
        self._id = id

    @property
    def title(self):
        return self._title

    #Вовзращаем название приоритета
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

    #Преобразование в словарь (для json)
    def to_dict(self):
        return {
            "title": self._title,
            "priority": self._priority.name,
            "isDone": self._is_done,
            "id": self._id,
        }

    #Преобразование из словаря (для чтения из записей в формате json из файла)
    @staticmethod
    def from_dict(data):
        return Task(data["title"],
                    Priority[data["priority"]],
                    data["isDone"],
                    data["id"]
                    )
