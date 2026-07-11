from __future__ import annotations

from ..movement_helper import (
    can_walk_through,
    can_walk_on,
    get_mining_duration_ticks,
    is_replaceable,
    is_water,
    is_lava,
)
from ..movement import Movement, MovementState
from ...movement.action_costs import (
    WALK_ONE_BLOCK_COST,
    FALL_N_BLOCKS_COST,
    CENTER_AFTER_FALL_COST,
    COST_INF,
)
from ....world.block_state import get_block_state_properties


class MovementFall(Movement):
    def __init__(self, context, start_x, start_y, start_z, direction, state=None):
        super().__init__(context, start_x, start_y, start_z, direction, state)

    def calculate(self) -> None:
        s = self.state
        s.dest_x = self.start_x
        s.dest_z = self.start_z

        max_fall = self.context.settings.max_fall_height_no_water
        if self.context.has_water_bucket and self.context.settings.allow_water_bucket_fall:
            max_fall = self.context.settings.max_fall_height_bucket

        if not self.context.settings.allow_downward:
            s.cost = COST_INF
            return

        if max_fall <= 0:
            s.cost = COST_INF
            return

        s.cost = WALK_ONE_BLOCK_COST + CENTER_AFTER_FALL_COST

        fall_distance = 0
        current_y = self.start_y - 1

        while fall_distance < max_fall + 5:
            if current_y < self.context.bsi._min_y:
                s.cost = COST_INF
                return

            state_block = self.context.get(self.start_x, current_y, self.start_z)
            props = get_block_state_properties(state_block)

            if props.is_lava:
                s.cost = COST_INF
                return

            if can_walk_on(self.context.bsi, self.start_x, current_y, self.start_z, state_block):
                if fall_distance < self.context.settings.min_fall_height:
                    s.cost = COST_INF
                    return
                s.dest_y = current_y + 1
                s.cost += FALL_N_BLOCKS_COST[fall_distance]
                if fall_distance > self.context.settings.max_fall_height_no_water:
                    if not self.context.has_water_bucket:
                        s.cost = COST_INF
                        return
                return

            if not can_walk_through(self.context.bsi, self.start_x, current_y, self.start_z, state_block):
                break_time = get_mining_duration_ticks(self.context, self.start_x, current_y, self.start_z, state_block, True)
                if break_time >= COST_INF:
                    s.cost = COST_INF
                    return
                s.cost += break_time

            fall_distance += 1
            current_y -= 1

        s.cost = COST_INF
