from __future__ import annotations

import math


class BetterBlockPos:
    __slots__ = ('x', 'y', 'z')

    def __init__(self, x: int, y: int, z: int) -> None:
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def long_hash(x: int, y: int, z: int) -> int:
        h = 3241
        h = 3457689 * h + x
        h = 8734625 * h + y
        h = 2873465 * h + z
        return h

    def __hash__(self) -> int:
        return int(BetterBlockPos.long_hash(self.x, self.y, self.z))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, BetterBlockPos):
            return self.x == other.x and self.y == other.y and self.z == other.z
        return False

    def __repr__(self) -> str:
        return f"BetterBlockPos(x={self.x}, y={self.y}, z={self.z})"

    def above(self, n: int = 1) -> BetterBlockPos:
        if n == 0:
            return self
        return BetterBlockPos(self.x, self.y + n, self.z)

    def below(self, n: int = 1) -> BetterBlockPos:
        if n == 0:
            return self
        return BetterBlockPos(self.x, self.y - n, self.z)

    def north(self, n: int = 1) -> BetterBlockPos:
        if n == 0:
            return self
        return BetterBlockPos(self.x, self.y, self.z - n)

    def south(self, n: int = 1) -> BetterBlockPos:
        if n == 0:
            return self
        return BetterBlockPos(self.x, self.y, self.z + n)

    def east(self, n: int = 1) -> BetterBlockPos:
        if n == 0:
            return self
        return BetterBlockPos(self.x + n, self.y, self.z)

    def west(self, n: int = 1) -> BetterBlockPos:
        if n == 0:
            return self
        return BetterBlockPos(self.x - n, self.y, self.z)

    def distance_sq(self, other: BetterBlockPos) -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return dx * dx + dy * dy + dz * dz

    def distance_to(self, other: BetterBlockPos) -> float:
        return math.sqrt(self.distance_sq(other))

    def subtract(self, other: BetterBlockPos) -> BetterBlockPos:
        return BetterBlockPos(self.x - other.x, self.y - other.y, self.z - other.z)

    def offset(self, dx: int, dy: int, dz: int) -> BetterBlockPos:
        return BetterBlockPos(self.x + dx, self.y + dy, self.z + dz)
