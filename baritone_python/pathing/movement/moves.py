from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .movement import Movement, MovementState
    from .calculation_context import CalculationContext


class Moves(Enum):
    DOWNWARD = (0, -1, 0, False, False, "DOWNWARD")
    PILLAR = (0, 1, 0, False, False, "PILLAR")
    TRAVERSE_NORTH = (0, 0, -1, False, False, "TRAVERSE_NORTH")
    TRAVERSE_SOUTH = (0, 0, 1, False, False, "TRAVERSE_SOUTH")
    TRAVERSE_EAST = (1, 0, 0, False, False, "TRAVERSE_EAST")
    TRAVERSE_WEST = (-1, 0, 0, False, False, "TRAVERSE_WEST")
    ASCEND_NORTH = (0, 1, -1, False, False, "ASCEND_NORTH")
    ASCEND_SOUTH = (0, 1, 1, False, False, "ASCEND_SOUTH")
    ASCEND_EAST = (1, 1, 0, False, False, "ASCEND_EAST")
    ASCEND_WEST = (-1, 1, 0, False, False, "ASCEND_WEST")
    DESCEND_NORTH = (0, -1, -1, False, False, "DESCEND_NORTH")
    DESCEND_SOUTH = (0, -1, 1, False, False, "DESCEND_SOUTH")
    DESCEND_EAST = (1, -1, 0, False, False, "DESCEND_EAST")
    DESCEND_WEST = (-1, -1, 0, False, False, "DESCEND_WEST")
    DIAGONAL_NORTHEAST = (1, 0, -1, False, False, "DIAGONAL_NORTHEAST")
    DIAGONAL_NORTHWEST = (-1, 0, -1, False, False, "DIAGONAL_NORTHWEST")
    DIAGONAL_SOUTHEAST = (1, 0, 1, False, False, "DIAGONAL_SOUTHEAST")
    DIAGONAL_SOUTHWEST = (-1, 0, 1, False, False, "DIAGONAL_SOUTHWEST")
    PARKOUR_NORTH = (0, 0, -2, False, False, "PARKOUR_NORTH")
    PARKOUR_SOUTH = (0, 0, 2, False, False, "PARKOUR_SOUTH")
    PARKOUR_EAST = (2, 0, 0, False, False, "PARKOUR_EAST")
    PARKOUR_WEST = (-2, 0, 0, False, False, "PARKOUR_WEST")

    def __init__(self, x_offset: int, y_offset: int, z_offset: int, dynamic_xz: bool, dynamic_y: bool, label: str):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.z_offset = z_offset
        self.dynamic_xz = dynamic_xz
        self.dynamic_y = dynamic_y
        self.label = label

    def get_mover(self, context: CalculationContext, start_x: int, start_y: int, start_z: int,
                  state: MovementState | None = None) -> Movement:
        from .movements.movement_traverse import MovementTraverse
        from .movements.movement_vertical import MovementDownward, MovementPillar
        from .movements.movement_ascend_descend import MovementAscend, MovementDescend
        from .movements.movement_diagonal import MovementDiagonal
        from .movements.movement_parkour import MovementParkour
        from .movements.movement_fall import MovementFall

        if self == Moves.DOWNWARD:
            return MovementDownward(context, start_x, start_y, start_z, 0, state)
        if self == Moves.PILLAR:
            return MovementPillar(context, start_x, start_y, start_z, 0, state)

        if self in (Moves.TRAVERSE_NORTH, Moves.TRAVERSE_SOUTH, Moves.TRAVERSE_EAST, Moves.TRAVERSE_WEST):
            return MovementTraverse(context, start_x, start_y, start_z, self._traverse_dir(), state)

        if self in (Moves.ASCEND_NORTH, Moves.ASCEND_SOUTH, Moves.ASCEND_EAST, Moves.ASCEND_WEST):
            return MovementAscend(context, start_x, start_y, start_z, self._ascend_dir(), state)

        if self in (Moves.DESCEND_NORTH, Moves.DESCEND_SOUTH, Moves.DESCEND_EAST, Moves.DESCEND_WEST):
            return MovementDescend(context, start_x, start_y, start_z, self._descend_dir(), state)

        if self in (Moves.DIAGONAL_NORTHEAST, Moves.DIAGONAL_NORTHWEST, Moves.DIAGONAL_SOUTHEAST, Moves.DIAGONAL_SOUTHWEST):
            return MovementDiagonal(context, start_x, start_y, start_z, self._diagonal_dir(), state)

        if self in (Moves.PARKOUR_NORTH, Moves.PARKOUR_SOUTH, Moves.PARKOUR_EAST, Moves.PARKOUR_WEST):
            return MovementParkour(context, start_x, start_y, start_z, self._parkour_dir(), state)

        raise ValueError(f"Unknown move type: {self}")

    def _traverse_dir(self) -> int:
        if self == Moves.TRAVERSE_EAST:
            return 0
        if self == Moves.TRAVERSE_WEST:
            return 1
        if self == Moves.TRAVERSE_SOUTH:
            return 2
        if self == Moves.TRAVERSE_NORTH:
            return 3
        return 0

    def _ascend_dir(self) -> int:
        if self == Moves.ASCEND_EAST:
            return 0
        if self == Moves.ASCEND_WEST:
            return 1
        if self == Moves.ASCEND_SOUTH:
            return 2
        if self == Moves.ASCEND_NORTH:
            return 3
        return 0

    def _descend_dir(self) -> int:
        if self == Moves.DESCEND_EAST:
            return 0
        if self == Moves.DESCEND_WEST:
            return 1
        if self == Moves.DESCEND_SOUTH:
            return 2
        if self == Moves.DESCEND_NORTH:
            return 3
        return 0

    def _diagonal_dir(self) -> int:
        if self == Moves.DIAGONAL_NORTHEAST:
            return 0
        if self == Moves.DIAGONAL_NORTHWEST:
            return 1
        if self == Moves.DIAGONAL_SOUTHEAST:
            return 2
        if self == Moves.DIAGONAL_SOUTHWEST:
            return 3
        return 0

    def _parkour_dir(self) -> int:
        if self == Moves.PARKOUR_EAST:
            return 0
        if self == Moves.PARKOUR_WEST:
            return 1
        if self == Moves.PARKOUR_SOUTH:
            return 2
        if self == Moves.PARKOUR_NORTH:
            return 3
        return 0
