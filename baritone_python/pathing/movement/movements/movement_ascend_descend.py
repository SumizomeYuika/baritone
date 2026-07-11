from __future__ import annotations

from ..movement_helper import (
    can_walk_through,
    can_walk_on,
    get_mining_duration_ticks,
    is_replaceable,
    can_place_against,
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


class MovementAscend(Movement):
    def __init__(self, context, start_x, start_y, start_z, direction, state=None):
        super().__init__(context, start_x, start_y, start_z, direction, state)

    def calculate(self) -> None:
        s = self.state
        dx, dz = DIRS[self.direction]
        s.dest_x = self.start_x + dx
        s.dest_y = self.start_y + 1
        s.dest_z = self.start_z + dz

        if not self.context.bsi.world_contains_loaded_chunk(s.dest_x, s.dest_z):
            s.cost = COST_INF
            return

        if not self.context.bsi.world_border.entirely_contains(s.dest_x, s.dest_z):
            s.cost = COST_INF
            return

        s.cost = WALK_ONE_BLOCK_COST + JUMP_ONE_BLOCK_COST + 0.63

        above_start = self.context.get(self.start_x, self.start_y + 1, self.start_z)
        if not can_walk_through(self.context.bsi, self.start_x, self.start_y + 1, self.start_z, above_start):
            s.cost += get_mining_duration_ticks(self.context, self.start_x, self.start_y + 1, self.start_z, above_start, True)
            if s.cost >= COST_INF:
                return

        two_above_start = self.context.get(self.start_x, self.start_y + 2, self.start_z)
        if not can_walk_through(self.context.bsi, self.start_x, self.start_y + 2, self.start_z, two_above_start):
            s.cost += get_mining_duration_ticks(self.context, self.start_x, self.start_y + 2, self.start_z, two_above_start, True)
            if s.cost >= COST_INF:
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
        if not can_walk_on(self.context.bsi, s.dest_x, s.dest_y - 1, s.dest_z, dest_floor):
            s.cost = COST_INF


class MovementDescend(Movement):
    def __init__(self, context, start_x, start_y, start_z, direction, state=None):
        super().__init__(context, start_x, start_y, start_z, direction, state)

    def calculate(self) -> None:
        s = self.state
        dx, dz = DIRS[self.direction]
        s.dest_x = self.start_x + dx
        s.dest_y = self.start_y - 1
        s.dest_z = self.start_z + dz

        if not self.context.bsi.world_contains_loaded_chunk(s.dest_x, s.dest_z):
            s.cost = COST_INF
            return

        if not self.context.bsi.world_border.entirely_contains(s.dest_x, s.dest_z):
            s.cost = COST_INF
            return

        s.cost = WALK_ONE_BLOCK_COST + CENTER_AFTER_FALL_COST

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

        corner = self.context.get(self.start_x + dx, self.start_y, self.start_z + dz)
        if not can_walk_through(self.context.bsi, self.start_x + dx, self.start_y, self.start_z + dz, corner):
            break_time = get_mining_duration_ticks(self.context, self.start_x + dx, self.start_y, self.start_z + dz, corner, True)
            if break_time >= COST_INF:
                s.cost = COST_INF
                return
            s.cost += break_time
