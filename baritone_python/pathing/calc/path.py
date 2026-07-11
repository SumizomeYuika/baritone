from __future__ import annotations

from typing import TYPE_CHECKING
from enum import Enum

from ...api.utils.better_block_pos import BetterBlockPos

if TYPE_CHECKING:
    from .path_node import PathNode


class PathCalculationResultType(Enum):
    SUCCESS_TO_GOAL = 0
    SUCCESS_SEGMENT = 1
    FAILURE = 2
    CANCELED = 3
    EXCEPTION = 4


class IPath:
    def __init__(self) -> None:
        pass

    def positions(self) -> list[BetterBlockPos]:
        raise NotImplementedError

    def length(self) -> int:
        raise NotImplementedError

    def get_src(self) -> BetterBlockPos:
        raise NotImplementedError

    def get_dest(self) -> BetterBlockPos:
        raise NotImplementedError


class Path(IPath):
    def __init__(
        self,
        real_start: BetterBlockPos,
        start_node: PathNode,
        end_node: PathNode,
        num_nodes_considered: int,
    ) -> None:
        super().__init__()
        self._real_start = real_start
        self._start_node = start_node
        self._end_node = end_node
        self._num_nodes_considered = num_nodes_considered
        self._positions: list[BetterBlockPos] | None = None
        self._nodes: list[PathNode] | None = None

    def positions(self) -> list[BetterBlockPos]:
        if self._positions is None:
            self._positions = [BetterBlockPos(n.x, n.y, n.z) for n in self.nodes()]
        return self._positions

    def nodes(self) -> list[PathNode]:
        if self._nodes is None:
            nodes = []
            current = self._end_node
            while current is not None:
                nodes.append(current)
                current = current.previous
            nodes.reverse()
            self._nodes = nodes
        return self._nodes

    def length(self) -> int:
        return len(self.positions())

    def get_src(self) -> BetterBlockPos:
        return self._real_start

    def get_dest(self) -> BetterBlockPos:
        return BetterBlockPos(self._end_node.x, self._end_node.y, self._end_node.z)

    @property
    def num_nodes_considered(self) -> int:
        return self._num_nodes_considered

    @property
    def cost(self) -> float:
        return self._end_node.cost

    def __repr__(self) -> str:
        return f"Path(src={self.get_src()}, dest={self.get_dest()}, length={self.length()}, cost={self.cost:.2f})"
