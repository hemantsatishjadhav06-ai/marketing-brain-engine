"""Store interface every control plane implements. Records are plain dicts with 'id'."""
from abc import ABC, abstractmethod


class Store(ABC):
    name = "base"

    @abstractmethod
    def list(self, table, where=None): ...

    @abstractmethod
    def create(self, table, fields): ...

    @abstractmethod
    def update(self, table, record_id, fields): ...

    def find_status(self, table, status):
        return [r for r in self.list(table) if r.get("fields", {}).get("Status") == status]
