from __future__ import annotations

from enum import Enum

from ...world.block_state_interface import BlockStateInterface
from ...world.block_state import get_block_state_properties
from .action_costs import COST_INF


class _Ternary(Enum):
    YES = 1
    NO = 2
    MAYBE = 3


class Ternary(Enum):
    YES = 1
    NO = 2
    MAYBE = 3


def is_water(blockstate_id: int) -> bool:
    props = get_block_state_properties(blockstate_id)
    return props.is_water


def is_lava(blockstate_id: int) -> bool:
    props = get_block_state_properties(blockstate_id)
    return props.is_lava


def is_liquid(blockstate_id: int) -> bool:
    props = get_block_state_properties(blockstate_id)
    return props.is_liquid


def is_block_normal_cube(blockstate_id: int) -> bool:
    props = get_block_state_properties(blockstate_id)
    return props.is_solid and not props.is_honey_block and not props.is_bubble_column


def can_walk_through_block_state(blockstate_id: int) -> Ternary:
    props = get_block_state_properties(blockstate_id)
    if props.is_air:
        return Ternary.YES
    if props.is_fire or props.is_cobweb or props.is_end_portal or props.is_honey_block:
        return Ternary.NO
    if props.is_door:
        if props.is_iron_door:
            return Ternary.NO
        return Ternary.YES
    if props.is_liquid:
        return Ternary.MAYBE
    if props.is_snow:
        return Ternary.MAYBE
    if props.can_be_replaced and not props.is_solid:
        return Ternary.YES
    return Ternary.NO


def can_walk_through(bsi: BlockStateInterface, x: int, y: int, z: int, blockstate_id: int | None = None) -> bool:
    if blockstate_id is None:
        blockstate_id = bsi.get0(x, y, z)
    result = can_walk_through_block_state(blockstate_id)
    if result == Ternary.YES:
        return True
    if result == Ternary.NO:
        return False
    props = get_block_state_properties(blockstate_id)
    if props.is_snow:
        if not bsi.world_contains_loaded_chunk(x, z):
            return True
        if props.snow_layers is not None and props.snow_layers >= 3:
            return False
        return can_walk_on(bsi, x, y - 1, z)
    if props.is_water:
        if is_flowing(bsi, x, y, z, blockstate_id):
            return False
        up_state = bsi.get0(x, y + 1, z)
        up_props = get_block_state_properties(up_state)
        if up_props.is_liquid:
            return False
        return props.is_water
    return False


def can_walk_on_block_state(blockstate_id: int) -> Ternary:
    props = get_block_state_properties(blockstate_id)
    if is_block_normal_cube(blockstate_id):
        return Ternary.YES
    if props.is_ladder or props.is_vine:
        return Ternary.YES
    if props.is_soul_sand:
        return Ternary.YES
    if props.is_slab:
        return Ternary.YES
    if props.is_water:
        return Ternary.MAYBE
    if props.is_lava:
        return Ternary.MAYBE
    return Ternary.NO


def can_walk_on(bsi: BlockStateInterface, x: int, y: int, z: int, blockstate_id: int | None = None) -> bool:
    if blockstate_id is None:
        blockstate_id = bsi.get0(x, y, z)
    result = can_walk_on_block_state(blockstate_id)
    if result == Ternary.YES:
        return True
    if result == Ternary.NO:
        return False
    props = get_block_state_properties(blockstate_id)
    if props.is_water:
        up_state = bsi.get0(x, y + 1, z)
        up_props = get_block_state_properties(up_state)
        if is_flowing(bsi, x, y, z, blockstate_id):
            return False
        return up_props.is_water
    if props.is_lava:
        if not is_flowing(bsi, x, y, z, blockstate_id):
            return True
    return False


def fully_passable_block_state(blockstate_id: int) -> Ternary:
    props = get_block_state_properties(blockstate_id)
    if props.is_air:
        return Ternary.YES
    if (props.is_fire or props.is_cobweb or props.is_vine or props.is_ladder
            or props.is_door or props.is_fence_gate or props.is_snow
            or props.is_liquid or props.is_end_portal):
        return Ternary.NO
    if props.can_be_replaced and not props.is_solid:
        return Ternary.YES
    return Ternary.NO


def fully_passable(bsi: BlockStateInterface, x: int, y: int, z: int, blockstate_id: int | None = None) -> bool:
    if blockstate_id is None:
        blockstate_id = bsi.get0(x, y, z)
    result = fully_passable_block_state(blockstate_id)
    if result == Ternary.YES:
        return True
    if result == Ternary.NO:
        return False
    return False


def is_replaceable(x: int, y: int, z: int, blockstate_id: int, bsi: BlockStateInterface) -> bool:
    props = get_block_state_properties(blockstate_id)
    if props.is_air:
        return True
    if props.is_snow:
        if not bsi.world_contains_loaded_chunk(x, z):
            return True
        return props.snow_layers == 1
    return props.can_be_replaced


def can_place_against(bsi: BlockStateInterface, x: int, y: int, z: int, blockstate_id: int | None = None) -> bool:
    if not bsi.world_border.can_place_at(x, z):
        return False
    if blockstate_id is None:
        blockstate_id = bsi.get0(x, y, z)
    return is_block_normal_cube(blockstate_id)


def avoid_breaking(bsi: BlockStateInterface, x: int, y: int, z: int, blockstate_id: int) -> bool:
    if not bsi.world_border.can_place_at(x, z):
        return True
    props = get_block_state_properties(blockstate_id)
    if props.is_ice or props.is_infested:
        return True
    if (avoid_adjacent_breaking(bsi, x, y + 1, z, True)
            or avoid_adjacent_breaking(bsi, x + 1, y, z, False)
            or avoid_adjacent_breaking(bsi, x - 1, y, z, False)
            or avoid_adjacent_breaking(bsi, x, y, z + 1, False)
            or avoid_adjacent_breaking(bsi, x, y, z - 1, False)):
        return True
    return False


def avoid_adjacent_breaking(bsi: BlockStateInterface, x: int, y: int, z: int, directly_above: bool) -> bool:
    state = bsi.get0(x, y, z)
    props = get_block_state_properties(state)
    if not directly_above and props.is_falling_block:
        below = bsi.get0(x, y - 1, z)
        below_props = get_block_state_properties(below)
        if below_props.is_air or below_props.can_be_replaced:
            return True
    if props.is_liquid:
        if directly_above:
            return True
        if props.water_level == 0:
            return True
        below = bsi.get0(x, y - 1, z)
        below_props = get_block_state_properties(below)
        return not below_props.is_liquid
    return False


def avoid_walking_into(blockstate_id: int) -> bool:
    props = get_block_state_properties(blockstate_id)
    return (props.is_liquid or props.is_magma_block or props.is_cactus
            or props.is_fire or props.is_end_portal or props.is_cobweb
            or props.is_bubble_column)


def must_be_solid_to_walk_on(blockstate_id: int) -> bool:
    props = get_block_state_properties(blockstate_id)
    if props.is_ladder or props.is_vine:
        return False
    if props.is_liquid:
        if props.is_slab and props.slab_type != "bottom":
            return True
        return True
    return True


def possibly_flowing(blockstate_id: int) -> bool:
    props = get_block_state_properties(blockstate_id)
    if not props.is_liquid:
        return False
    return props.water_level is not None and props.water_level != 8


def is_flowing(bsi: BlockStateInterface, x: int, y: int, z: int, blockstate_id: int) -> bool:
    props = get_block_state_properties(blockstate_id)
    if not props.is_liquid:
        return False
    if props.water_level is not None and props.water_level != 8:
        return True
    return (possibly_flowing(bsi.get0(x + 1, y, z))
            or possibly_flowing(bsi.get0(x - 1, y, z))
            or possibly_flowing(bsi.get0(x, y, z + 1))
            or possibly_flowing(bsi.get0(x, y, z - 1)))


def get_mining_duration_ticks(context, x: int, y: int, z: int, blockstate_id: int, include_falling: bool) -> float:
    if not can_walk_through(context.bsi, x, y, z, blockstate_id):
        props = get_block_state_properties(blockstate_id)
        if props.is_liquid:
            return COST_INF
        mult = context.break_cost_multiplier_at(x, y, z, blockstate_id)
        if mult >= COST_INF:
            return COST_INF
        if avoid_breaking(context.bsi, x, y, z, blockstate_id):
            return COST_INF
        str_vs_block = context.tool_set.get_str_vs_block(blockstate_id)
        if str_vs_block <= 0:
            return COST_INF
        result = 1.0 / str_vs_block
        result += context.break_block_additional_cost
        result *= mult
        if include_falling:
            above = context.get(x, y + 1, z)
            above_props = get_block_state_properties(above)
            if above_props.is_falling_block:
                result += get_mining_duration_ticks(context, x, y + 1, z, above, True)
        return result
    return 0.0


HORIZONTALS_BUT_ALSO_DOWN_____SO_EVERY_DIRECTION_EXCEPT_UP = [
    (1, 0, 0),
    (-1, 0, 0),
    (0, 0, 1),
    (0, 0, -1),
    (0, -1, 0),
]
