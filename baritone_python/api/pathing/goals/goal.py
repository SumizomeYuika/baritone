from __future__ import annotations

from abc import ABC, abstractmethod
import math


class Goal(ABC):
    @abstractmethod
    def is_in_goal(self, x: int, y: int, z: int) -> bool:
        ...

    @abstractmethod
    def heuristic(self, x: int, y: int, z: int) -> float:
        ...

    def __hash__(self) -> int:
        return 0

    def __eq__(self, other: object) -> bool:
        return self is other


class GoalBlock(Goal):
    def __init__(self, x: int, y: int, z: int) -> None:
        self.x = x
        self.y = y
        self.z = z

    def is_in_goal(self, x: int, y: int, z: int) -> bool:
        return x == self.x and y == self.y and z == self.z

    def heuristic(self, x: int, y: int, z: int) -> float:
        dx = self.x - x
        dy = self.y - y
        dz = self.z - z
        if dy > 0:
            return (math.sqrt(dx * dx + dz * dz) + dy) * 20
        return (math.sqrt(dx * dx + dz * dz) - dy) * 20

    def __repr__(self) -> str:
        return f"GoalBlock(x={self.x}, y={self.y}, z={self.z})"


class GoalXZ(Goal):
    def __init__(self, x: int, z: int) -> None:
        self.x = x
        self.z = z

    def is_in_goal(self, x: int, y: int, z: int) -> bool:
        return x == self.x and z == self.z

    def heuristic(self, x: int, y: int, z: int) -> float:
        dx = self.x - x
        dz = self.z - z
        return math.sqrt(dx * dx + dz * dz) * 20

    def __repr__(self) -> str:
        return f"GoalXZ(x={self.x}, z={self.z})"


class GoalYLevel(Goal):
    def __init__(self, y: int) -> None:
        self.y = y

    def is_in_goal(self, x: int, y: int, z: int) -> bool:
        return y == self.y

    def heuristic(self, x: int, y: int, z: int) -> float:
        dy = self.y - y
        return abs(dy) * 20

    def __repr__(self) -> str:
        return f"GoalYLevel(y={self.y})"


class GoalNear(Goal):
    def __init__(self, x: int, y: int, z: int, range_sq: float) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.range_sq = range_sq

    def is_in_goal(self, x: int, y: int, z: int) -> bool:
        dx = self.x - x
        dy = self.y - y
        dz = self.z - z
        return dx * dx + dy * dy + dz * dz <= self.range_sq

    def heuristic(self, x: int, y: int, z: int) -> float:
        dx = self.x - x
        dy = self.y - y
        dz = self.z - z
        if dy > 0:
            return (math.sqrt(dx * dx + dz * dz) + dy - math.sqrt(self.range_sq)) * 20
        return (math.sqrt(dx * dx + dz * dz) - dy - math.sqrt(self.range_sq)) * 20

    def __repr__(self) -> str:
        return f"GoalNear(x={self.x}, y={self.y}, z={self.z}, range_sq={self.range_sq})"


class GoalAxis(Goal):
    def __init__(self, x: int, z: int) -> None:
        self.x = x
        self.z = z

    def is_in_goal(self, x: int, y: int, z: int) -> bool:
        return x == self.x or z == self.z

    def heuristic(self, x: int, y: int, z: int) -> float:
        dx = abs(self.x - x)
        dz = abs(self.z - z)
        return min(dx, dz) * 20

    def __repr__(self) -> str:
        return f"GoalAxis(x={self.x}, z={self.z})"


class GoalInverted(Goal):
    def __init__(self, origin: Goal) -> None:
        self.origin = origin

    def is_in_goal(self, x: int, y: int, z: int) -> bool:
        return not self.origin.is_in_goal(x, y, z)

    def heuristic(self, x: int, y: int, z: int) -> float:
        if self.is_in_goal(x, y, z):
            return 0
        return -self.origin.heuristic(x, y, z)

    def __repr__(self) -> str:
        return f"GoalInverted(origin={self.origin})"
