from __future__ import annotations

from ..api.utils.better_block_pos import BetterBlockPos


class Favoring:
    __slots__ = ('favors',)

    def __init__(self) -> None:
        self.favors: dict[int, float] = {}

    def add_favor(self, pos: BetterBlockPos, multiplier: float) -> None:
        h = int(BetterBlockPos.long_hash(pos.x, pos.y, pos.z))
        self.favors[h] = multiplier

    def calculate(self, pos: BetterBlockPos) -> float:
        h = int(BetterBlockPos.long_hash(pos.x, pos.y, pos.z))
        return self.favors.get(h, 1.0)

    def is_empty(self) -> bool:
        return len(self.favors) == 0
