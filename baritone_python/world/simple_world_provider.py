from __future__ import annotations

from typing import Callable
from .block_state_provider import BlockStateProvider
from .block_state import get_block_state_properties


class SimpleWorldProvider(BlockStateProvider):
    AIR = 0
    STONE = 1
    DIRT = 3
    WATER = 5
    LAVA = 6

    def __init__(
        self,
        min_x: int = -64,
        max_x: int = 64,
        min_y: int = -64,
        max_y: int = 320,
        min_z: int = -64,
        max_z: int = 64,
    ) -> None:
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.min_z = min_z
        self.max_z = max_z
        self._blocks: dict[tuple[int, int, int], int] = {}
        self._generator: Callable[[int, int, int], int] | None = None

    def set_block(self, x: int, y: int, z: int, blockstate_id: int) -> None:
        self._blocks[(x, y, z)] = blockstate_id

    def set_generator(self, gen: Callable[[int, int, int], int]) -> None:
        self._generator = gen

    def get_block_state(self, x: int, y: int, z: int) -> int:
        key = (x, y, z)
        if key in self._blocks:
            return self._blocks[key]
        if self._generator is not None:
            return self._generator(x, y, z)
        if y < self.min_y or y >= self.max_y:
            return self.AIR
        if y == self.min_y:
            return self.STONE
        return self.AIR

    def is_loaded(self, x: int, z: int) -> bool:
        return self.min_x <= x < self.max_x and self.min_z <= z < self.max_z

    def get_world_border(self) -> tuple[float, float, float, float]:
        return (float(self.min_x), float(self.max_x), float(self.min_z), float(self.max_z))

    def dimension_min_y(self) -> int:
        return self.min_y

    def dimension_height(self) -> int:
        return self.max_y - self.min_y

    def fill_floor(self, y: int = 0) -> None:
        for x in range(self.min_x, self.max_x):
            for z in range(self.min_z, self.max_z):
                self.set_block(x, y, z, self.STONE)

    def add_wall(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, block: int = 1) -> None:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set_block(x, y, z, block)
