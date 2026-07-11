from __future__ import annotations

from ..movement_helper import (
    can_walk_through,
    can_walk_on,
    get_mining_duration_ticks,
    is_replaceable,
)
from ..movement import Movement, MovementState
from .movement_traverse import DIRS
from ...movement.action_costs import (
    WALK_ONE_BLOCK_COST,
    JUMP_ONE_BLOCK_COST,
    CENTER_AFTER_FALL_COST,
    COST_INF,
)
from ....world.block_state import get_block_state_properties


class MovementParkour(Movement):
    def __init__(self, context, start_x, start_y, start_z, direction, state=None):
        super().__init__(context, start_x, start_y, start_z, direction, state)

    def calculate(self) -> None:
        s = self.state
        dx, dz = DIRS[self.direction]

        if not self.context.settings.allow_parkour:
            s.cost = COST_INF
            return

        s.dest_x = self.start_x + dx * 2
        s.dest_y = self.start_y
        s.dest_z = self.start_z + dz * 2

        if not self.context.bsi.world_contains_loaded_chunk(s.dest_x, s.dest_z):
            s.cost = COST_INF
            return

        if not self.context.bsi.world_border.entirely_contains(s.dest_x, s.dest_z):
            s.cost = COST_INF
            return

        s.cost = WALK_ONE_BLOCK_COST * 2 + JUMP_ONE_BLOCK_COST

        mid_x = self.start_x + dx
        mid_z = self.start_z + dz

        for y_off in range(3):
            mid_state = self.context.get(mid_x, self.start_y + y_off - 1, mid_z)
            if y_off < 2:
                if not can_walk_through(self.context.bsi, mid_x, self.start_y + y_off, mid_z, mid_state):
                    s.cost = COST_INF
                    return
            else:
                head_state = self.context.get(mid_x, self.start_y + y_off, mid_z)
                if not can_walk_through(self.context.bsi, mid_x, self.start_y + y_off, mid_z, head_state):
                    s.cost = COST_INF
                    return

        dest_foot = self.context.get(s.dest_x, s.dest_y, s.dest_z)
        if not can_walk_through(self.context.bsi, s.dest_x, s.dest_y, s.dest_z, dest_foot):
            s.cost = COST_INF
            return

        dest_head = self.context.get(s.dest_x, s.dest_y + 1, s.dest_z)
        if not can_walk_through(self.context.bsi, s.dest_x, s.dest_y + 1, s.dest_z, dest_head):
            s.cost = COST_INF
            return

        dest_floor = self.context.get(s.dest_x, s.dest_y - 1, s.dest_z)
        if not can_walk_on(self.context.bsi, s.dest_x, s.dest_y - 1, s.dest_z, dest_floor):
            if not self.context.settings.allow_parkour_place:
                s.cost = COST_INF
                return
            if is_replaceable(s.dest_x, s.dest_y - 1, s.dest_z, dest_floor, self.context.bsi):
                place_cost = self.context.cost_of_placing_at(s.dest_x, s.dest_y - 1, s.dest_z, dest_floor)
                if place_cost >= COST_INF:
                    s.cost = COST_INF
                    return
                s.cost += place_cost
            else:
                s.cost = COST_INF
                return
