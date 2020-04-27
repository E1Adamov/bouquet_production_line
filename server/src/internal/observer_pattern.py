from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def update(self, arg):
        pass


class Observable(ABC):
    def __init__(self):
        self.observers = list()

    def add_observer(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def delete_observer(self, observer):
        self.observers.remove(observer)

    async def notify_observers(self, *a, **kw):
        except_ = kw.get('except_', set())

        if except_:
            del kw['except_']

        for observer in self.observers:
            if observer in except_:
                continue
            await observer.update(*a, **kw)
