from __future__ import annotations

import math


WALK_ONE_BLOCK_COST = 20 / 4.317
WALK_ONE_IN_WATER_COST = 20 / 2.2
WALK_ONE_OVER_SOUL_SAND_COST = WALK_ONE_BLOCK_COST * 2
LADDER_UP_ONE_COST = 20 / 2.35
LADDER_DOWN_ONE_COST = 20 / 3.0
SNEAK_ONE_BLOCK_COST = 20 / 1.3
SPRINT_ONE_BLOCK_COST = 20 / 5.612
SPRINT_MULTIPLIER = SPRINT_ONE_BLOCK_COST / WALK_ONE_BLOCK_COST
WALK_OFF_BLOCK_COST = WALK_ONE_BLOCK_COST * 0.8
CENTER_AFTER_FALL_COST = WALK_ONE_BLOCK_COST - WALK_OFF_BLOCK_COST

COST_INF = 1000000.0


def _velocity(ticks: int) -> float:
    return (math.pow(0.98, ticks) - 1) * -3.92


def _distance_to_ticks(distance: float) -> float:
    if distance == 0:
        return 0.0
    tmp_distance = distance
    tick_count = 0
    while True:
        fall_distance = _velocity(tick_count)
        if tmp_distance <= fall_distance:
            return tick_count + tmp_distance / fall_distance
        tmp_distance -= fall_distance
        tick_count += 1


def _generate_fall_n_blocks_cost() -> list[float]:
    costs = []
    for i in range(4097):
        costs.append(_distance_to_ticks(i))
    return costs


FALL_N_BLOCKS_COST = _generate_fall_n_blocks_cost()

FALL_1_25_BLOCKS_COST = _distance_to_ticks(1.25)
FALL_0_25_BLOCKS_COST = _distance_to_ticks(0.25)
JUMP_ONE_BLOCK_COST = FALL_1_25_BLOCKS_COST - FALL_0_25_BLOCKS_COST
