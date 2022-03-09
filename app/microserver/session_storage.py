from abc import ABC, abstractmethod
from flask import session
from typing import Optional, Any, Dict

from .utils import ThreadSafe, thread_safe

# TODO: cleanup

class Storable(ABC):
    @abstractmethod
    def is_alive(self):
        pass

    @abstractmethod
    def kill(self):
        pass

    @property
    def id(self):
        return id(self)


class SessionStorage(ThreadSafe):
    def __init__(self, name: str, allow_dead: bool = True, map: Dict[Any, Storable] = None):
        super().__init__()
        self.name = name
        self.allow_dead = allow_dead
        self.map = map or {}

    @thread_safe
    def store(self, obj: Storable) -> None:
        if not self.allow_dead and not obj.is_alive():
            raise ValueError
        self.remove()
        self.map[obj.id] = obj
        session[self.name] = obj.id

    @thread_safe
    def _remove(self) -> Optional[Storable]:
        current = self._get()
        if current is not None:
            del self.map[current.id]
        return current

    @thread_safe
    def remove(self) -> None:
        obj = self._remove()
        if obj is not None:
            obj.kill()

    @thread_safe
    def _get(self) -> Optional[Storable]:
        oid = session.get(self.name)
        if oid is None:
            return None
        current = self.map.get(oid)
        if current is None:
            del session[self.name]
        return current

    @thread_safe
    def get(self) -> Optional[Storable]:
        obj = self._get()
        if not self.allow_dead and obj is not None and not obj.is_alive():
            self._remove()
            obj = None
        return obj

    def exists(self) -> bool:
        return self.get() is not None
