from __future__ import annotations

from abc import ABC, abstractmethod

from ..path_node import PathNode


class IOpenSet(ABC):
    @abstractmethod
    def insert(self, node: PathNode) -> None:
        ...

    @abstractmethod
    def is_empty(self) -> bool:
        ...

    @abstractmethod
    def remove_lowest(self) -> PathNode:
        ...

    @abstractmethod
    def update(self, node: PathNode) -> None:
        ...
