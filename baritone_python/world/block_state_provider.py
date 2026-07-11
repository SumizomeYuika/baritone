from abc import ABC, abstractmethod


class BlockStateProvider(ABC):
    @abstractmethod
    def get_block_state(self, x: int, y: int, z: int) -> int:
        ...

    @abstractmethod
    def is_loaded(self, x: int, z: int) -> bool:
        ...

    @abstractmethod
    def get_world_border(self) -> tuple[float, float, float, float]:
        ...

    @abstractmethod
    def dimension_min_y(self) -> int:
        ...

    @abstractmethod
    def dimension_height(self) -> int:
        ...
