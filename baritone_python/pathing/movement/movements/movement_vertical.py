from __future__ import annotations

from ..movement_helper import (
    can_walk_through,
    can_walk_on,
    get_mining_duration_ticks,
    is_replaceable,
    can_place_against,
    avoid_breaking,
    is_water,
    is_lava,
)
from ..movement import Movement, MovementState
from ..action_costs import (
    WALK_ONE_BLOCK_COST,
    WALK_ONE_IN_WATER_COST,
    FALL_N_BLOCKS_COST,
    JUMP_ONE_BLOCK_COST,
    CENTER_AFTER_FALL_COST,
    COST_INF,
)
from ....world.block_state import get_block_state_properties


class MovementDownward(Movement):
    def __init__(self, context, start_x, start_y, start_z, direction, state=None):
        super().__init__(context, start_x, start_y, start_z, direction, state)

    def calculate(self) -> None:
        s = self.state
        if not self.context.settings.allow_downward:
            s.cost = COST_INF
            return
        s.dest_x = self.start_x
        s.dest_y = self.start_y - 1
        s.dest_z = self.start_z
        s.cost = WALK_ONE_BLOCK_COST
        fall_start = get_mining_duration_ticks(self.context, self.start_x, self.start_y - 1, self.start_z,
                                               self.context.get(self.start_x, self.start_y - 1, self.start_z), True)
        if fall_start >= COST_INF:
            s.cost = COST_INF
            return
        s.cost += fall_start
        if not is_replaceable(self.start_x, self.start_y - 2, self.start_z,
                              self.context.get(self.start_x, self.start_y - 2, self.start_z), self.context.bsi):
            landing_state = self.context.get(self.start_x, self.start_y - 2, self.start_z)
            if not can_walk_on(self.context.bsi, self.start_x, self.start_y - 2, self.start_z, landing_state):
                s.cost = COST_INF
                return
            landing_props = get_block_state_properties(landing_state)
            if landing_props.is_lava and not self.context.settings.assume_walk_on_lava:
                s.cost = COST_INF
                return


class MovementPillar(Movement):
    def __init__(self, context, start_x, start_y, start_z, direction, state=None):
        super().__init__(context, start_x, start_y, start_z, direction, state)

    def calculate(self) -> None:
        s = self.state
        if not self.context.has_throwaway:
            s.cost = COST_INF
            return
        if not self.context.settings.allow_place:
            s.cost = COST_INF
            return
        if self.context.settings.allow_only_downward:
            s.cost = COST_INF
            return
        s.dest_x = self.start_x
        s.dest_y = self.start_y + 1
        s.dest_z = self.start_z
        s.cost = WALK_ONE_BLOCK_COST + JUMP_ONE_BLOCK_COST
        start_top = self.context.get(self.start_x, self.start_y + 1, self.start_z)
        if not can_walk_through(self.context.bsi, self.start_x, self.start_y + 1, self.start_z, start_top):
            break_time = get_mining_duration_ticks(self.context, self.start_x, self.start_y + 1, self.start_z, start_top, True)
            if break_time >= COST_INF:
                s.cost = COST_INF
                return
            s.cost += break_time
        s.cost += self.context.cost_of_placing_at(self.start_x, self.start_y - 1, self.start_z,
                                                   self.context.get(self.start_x, self.start_y - 1, self.start_z))
        if s.cost >= COST_INF:
            return
        foot_state = self.context.get(self.start_x, self.start_y, self.start_z)
        if is_replaceable(self.start_x, self.start_y, self.start_z, foot_state, self.context.bsi):
            if not can_place_against(self.context.bsi, self.start_x, self.start_y - 1, self.start_z):
                s.cost = COST_INF
