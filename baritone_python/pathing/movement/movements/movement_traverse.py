from __future__ import annotations

from ..movement_helper import (
    can_walk_through,
    can_walk_on,
    get_mining_duration_ticks,
    is_replaceable,
    can_place_against,
    is_water,
    is_lava,
    avoid_breaking,
    avoid_walking_into,
    fully_passable,
)
from ..movement import Movement, MovementState
from ...movement.action_costs import (
    WALK_ONE_BLOCK_COST,
    WALK_ONE_IN_WATER_COST,
    JUMP_ONE_BLOCK_COST,
    FALL_0_25_BLOCKS_COST,
    CENTER_AFTER_FALL_COST,
    COST_INF,
)
from ....world.block_state import get_block_state_properties

DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


class MovementTraverse(Movement):
    def __init__(self, context, start_x, start_y, start_z, direction, state=None):
        super().__init__(context, start_x, start_y, start_z, direction, state)

    def calculate(self) -> None:
        s = self.state
        dx, dz = DIRS[self.direction]
        s.dest_x = self.start_x + dx
        s.dest_y = self.start_y
        s.dest_z = self.start_z + dz

        if not self.context.bsi.world_contains_loaded_chunk(s.dest_x, s.dest_z):
            s.cost = COST_INF
            return

        if not self.context.bsi.world_border.entirely_contains(s.dest_x, s.dest_z):
            s.cost = COST_INF
            return

        current_feet = self.context.get(self.start_x, self.start_y, self.start_z)
        current_feet_props = get_block_state_properties(current_feet)
        current_head = self.context.get(self.start_x, self.start_y + 1, self.start_z)
        current_head_props = get_block_state_properties(current_head)

        in_water = current_feet_props.is_water or current_head_props.is_water

        if in_water:
            s.cost = WALK_ONE_IN_WATER_COST
        else:
            s.cost = WALK_ONE_BLOCK_COST

        dest_foot = self.context.get(s.dest_x, s.dest_y, s.dest_z)
        dest_head = self.context.get(s.dest_x, s.dest_y + 1, s.dest_z)

        if not can_walk_through(self.context.bsi, s.dest_x, s.dest_y, s.dest_z, dest_foot):
            break_time = get_mining_duration_ticks(self.context, s.dest_x, s.dest_y, s.dest_z, dest_foot, True)
            if break_time >= COST_INF:
                s.cost = COST_INF
                return
            s.cost += break_time

        if not can_walk_through(self.context.bsi, s.dest_x, s.dest_y + 1, s.dest_z, dest_head):
            break_time = get_mining_duration_ticks(self.context, s.dest_x, s.dest_y + 1, s.dest_z, dest_head, True)
            if break_time >= COST_INF:
                s.cost = COST_INF
                return
            s.cost += break_time

        dest_floor = self.context.get(s.dest_x, s.dest_y - 1, s.dest_z)
        dest_floor_props = get_block_state_properties(dest_floor)

        if can_walk_on(self.context.bsi, s.dest_x, s.dest_y - 1, s.dest_z, dest_floor):
            walk_on_cost = 0
            if dest_floor_props.is_soul_sand:
                walk_on_cost = WALK_ONE_BLOCK_COST
            s.cost += walk_on_cost
        else:
            if is_replaceable(s.dest_x, s.dest_y - 1, s.dest_z, dest_floor, self.context.bsi):
                place_cost = self.context.cost_of_placing_at(s.dest_x, s.dest_y - 1, s.dest_z, dest_floor)
                if place_cost >= COST_INF:
                    s.cost = COST_INF
                    return
                s.cost += place_cost
                if not self._can_place_block(s.dest_x, s.dest_y - 1, s.dest_z):
                    s.cost = COST_INF
                    return
            else:
                s.cost = COST_INF
                return

        dest_head_props = get_block_state_properties(dest_head)
        if (dest_head_props.is_lava or dest_head_props.is_fire or dest_head_props.is_magma_block
                or dest_head_props.is_cactus or dest_head_props.is_end_portal or dest_head_props.is_cobweb):
            if not self.context.settings.assume_walk_on_lava:
                if not self.context.settings.allow_walk_on_magma_blocks:
                    pass

    def _can_place_block(self, x: int, y: int, z: int) -> bool:
        if not self.context.has_throwaway:
            return False
        if not self.context.settings.allow_place:
            return False
        if not self.context.settings.place_blocks_against_blocks:
            return True
        for dx, dy, dz in [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 0, -1), (0, 0, 1)]:
            nx, ny, nz = x + dx, y + dy, z + dz
            state = self.context.get(nx, ny, nz)
            if can_place_against(self.context.bsi, nx, ny, nz, state):
                return True
        return False
