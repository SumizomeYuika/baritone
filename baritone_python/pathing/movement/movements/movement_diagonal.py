from __future__ import annotations

from ..movement_helper import (
    can_walk_through,
    can_walk_on,
    get_mining_duration_ticks,
    is_replaceable,
)
from ..movement import Movement, MovementState
from ...movement.action_costs import (
    WALK_ONE_BLOCK_COST,
    WALK_ONE_IN_WATER_COST,
    COST_INF,
)
from ....world.block_state import get_block_state_properties

DIAGONAL_DIRS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]


class MovementDiagonal(Movement):
    def __init__(self, context, start_x, start_y, start_z, direction, state=None):
        super().__init__(context, start_x, start_y, start_z, direction, state)

    def calculate(self) -> None:
        s = self.state
        dx, dz = DIAGONAL_DIRS[self.direction]
        s.dest_x = self.start_x + dx
        s.dest_y = self.start_y
        s.dest_z = self.start_z + dz

        if not self.context.settings.allow_diagonal_descend:
            s.cost = COST_INF
            return

        if not self.context.bsi.world_contains_loaded_chunk(s.dest_x, s.dest_z):
            s.cost = COST_INF
            return

        if not self.context.bsi.world_border.entirely_contains(s.dest_x, s.dest_z):
            s.cost = COST_INF
            return

        s.cost = WALK_ONE_BLOCK_COST * 1.4142135623730951

        x1 = self.start_x + dx
        z1 = self.start_z
        x2 = self.start_x
        z2 = self.start_z + dz

        side1_foot = self.context.get(x1, self.start_y, z1)
        side2_foot = self.context.get(x2, self.start_y, z2)

        if not can_walk_through(self.context.bsi, x1, self.start_y, z1, side1_foot):
            if not can_walk_through(self.context.bsi, x2, self.start_y, z2, side2_foot):
                s.cost = COST_INF
                return

        side1_head = self.context.get(x1, self.start_y + 1, z1)
        side2_head = self.context.get(x2, self.start_y + 1, z2)

        if not can_walk_through(self.context.bsi, x1, self.start_y + 1, z1, side1_head):
            if not can_walk_through(self.context.bsi, x2, self.start_y + 1, z2, side2_head):
                s.cost = COST_INF
                return

        dest_foot = self.context.get(s.dest_x, s.dest_y, s.dest_z)
        if not can_walk_through(self.context.bsi, s.dest_x, s.dest_y, s.dest_z, dest_foot):
            break_time = get_mining_duration_ticks(self.context, s.dest_x, s.dest_y, s.dest_z, dest_foot, True)
            if break_time >= COST_INF:
                s.cost = COST_INF
                return
            s.cost += break_time

        dest_head = self.context.get(s.dest_x, s.dest_y + 1, s.dest_z)
        if not can_walk_through(self.context.bsi, s.dest_x, s.dest_y + 1, s.dest_z, dest_head):
            break_time = get_mining_duration_ticks(self.context, s.dest_x, s.dest_y + 1, s.dest_z, dest_head, True)
            if break_time >= COST_INF:
                s.cost = COST_INF
                return
            s.cost += break_time

        dest_floor = self.context.get(s.dest_x, s.dest_y - 1, s.dest_z)
        if can_walk_on(self.context.bsi, s.dest_x, s.dest_y - 1, s.dest_z, dest_floor):
            return
        else:
            if is_replaceable(s.dest_x, s.dest_y - 1, s.dest_z, dest_floor, self.context.bsi):
                place_cost = self.context.cost_of_placing_at(s.dest_x, s.dest_y - 1, s.dest_z, dest_floor)
                if place_cost >= COST_INF:
                    s.cost = COST_INF
                    return
                s.cost += place_cost
            else:
                s.cost = COST_INF
                return
