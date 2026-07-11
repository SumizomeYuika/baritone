from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ...api.utils.better_block_pos import BetterBlockPos

if TYPE_CHECKING:
    from .calculation_context import CalculationContext


class MovementState:
    def __init__(self) -> None:
        self.dest_x: int = 0
        self.dest_y: int = 0
        self.dest_z: int = 0
        self.cost: float = 0.0
        self.ready: bool = False


class Movement(ABC):
    def __init__(
        self,
        context: CalculationContext,
        start_x: int,
        start_y: int,
        start_z: int,
        direction: int,
        state: MovementState | None = None,
    ) -> None:
        self.context = context
        self.start_x = start_x
        self.start_y = start_y
        self.start_z = start_z
        self.direction = direction
        self.state = state or MovementState()
        if not self.state.ready:
            self._reset(state)
            self.calculate()
            state.ready = True

    def _reset(self, state: MovementState) -> None:
        state.dest_x = self.start_x
        state.dest_y = self.start_y
        state.dest_z = self.start_z
        state.cost = 0.0
        state.ready = False

    @abstractmethod
    def calculate(self) -> None:
        ...

    @property
    def dest_x(self) -> int:
        return self.state.dest_x

    @property
    def dest_y(self) -> int:
        return self.state.dest_y

    @property
    def dest_z(self) -> int:
        return self.state.dest_z

    @property
    def cost(self) -> float:
        return self.state.cost

    def get_src(self) -> BetterBlockPos:
        return BetterBlockPos(self.start_x, self.start_y, self.start_z)

    def get_dest(self) -> BetterBlockPos:
        return BetterBlockPos(self.dest_x, self.dest_y, self.dest_z)

    def override(self, new_cost: float) -> None:
        self.state.cost = new_cost
