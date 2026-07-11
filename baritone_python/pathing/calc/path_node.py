from __future__ import annotations

from typing import TYPE_CHECKING

from ..movement.action_costs import COST_INF
from ...api.utils.better_block_pos import BetterBlockPos

if TYPE_CHECKING:
    from ...api.pathing.goals.goal import Goal


class PathNode:
    __slots__ = (
        'x', 'y', 'z',
        'estimated_cost_to_goal',
        'cost',
        'combined_cost',
        'previous',
        'heap_position',
    )

    def __init__(self, x: int, y: int, z: int, goal: Goal) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.estimated_cost_to_goal = goal.heuristic(x, y, z)
        self.cost = COST_INF
        self.combined_cost = COST_INF
        self.previous: PathNode | None = None
        self.heap_position: int = -1

    def is_open(self) -> bool:
        return self.heap_position != -1

    def __hash__(self) -> int:
        return int(BetterBlockPos.long_hash(self.x, self.y, self.z))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PathNode):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __repr__(self) -> str:
        return f"PathNode(x={self.x}, y={self.y}, z={self.z}, cost={self.cost})"
