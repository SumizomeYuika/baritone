from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BlockStateProperties:
    block_id: int = 0
    is_air: bool = True
    is_solid: bool = False
    is_water: bool = False
    is_lava: bool = False
    is_liquid: bool = False
    water_level: int | None = None
    is_slab: bool = False
    slab_type: str | None = None
    is_stairs: bool = False
    stair_half: str | None = None
    is_door: bool = False
    is_door_open: bool = False
    is_iron_door: bool = False
    is_fence_gate: bool = False
    is_fence_gate_open: bool = False
    is_ladder: bool = False
    is_vine: bool = False
    is_snow: bool = False
    snow_layers: int | None = None
    is_soul_sand: bool = False
    is_magma_block: bool = False
    is_cactus: bool = False
    is_falling_block: bool = False
    is_fire: bool = False
    is_cobweb: bool = False
    is_end_portal: bool = False
    is_honey_block: bool = False
    is_bubble_column: bool = False
    is_ice: bool = False
    is_infested: bool = False
    can_be_replaced: bool = True
    hardness: float = 0.0


_AIR_PROPS = BlockStateProperties(is_air=True, can_be_replaced=True, hardness=0.0)

_BLOCKSTATE_PROPS: dict[int, BlockStateProperties] = {}


def get_block_state_properties(blockstate_id: int) -> BlockStateProperties:
    return _BLOCKSTATE_PROPS.get(blockstate_id, _AIR_PROPS)


def register_block_state(blockstate_id: int, props: BlockStateProperties) -> None:
    _BLOCKSTATE_PROPS[blockstate_id] = props


def init_default_blockstates() -> None:
    _BLOCKSTATE_PROPS[0] = BlockStateProperties(is_air=True, can_be_replaced=True, hardness=0.0)
    _BLOCKSTATE_PROPS[1] = BlockStateProperties(
        block_id=1, is_air=False, is_solid=True, can_be_replaced=False, hardness=1.5
    )
    _BLOCKSTATE_PROPS[2] = BlockStateProperties(
        block_id=2, is_air=False, is_solid=True, is_falling_block=True, can_be_replaced=False, hardness=0.5
    )
    _BLOCKSTATE_PROPS[3] = BlockStateProperties(
        block_id=3, is_air=False, is_solid=True, is_falling_block=True, can_be_replaced=False, hardness=0.6
    )
    _BLOCKSTATE_PROPS[4] = BlockStateProperties(
        block_id=4, is_air=False, is_solid=True, can_be_replaced=False, hardness=2.0
    )
    _BLOCKSTATE_PROPS[5] = BlockStateProperties(
        block_id=5, is_air=False, is_water=True, is_liquid=True, water_level=8, can_be_replaced=True, hardness=100.0
    )
    _BLOCKSTATE_PROPS[6] = BlockStateProperties(
        block_id=6, is_air=False, is_lava=True, is_liquid=True, can_be_replaced=True, hardness=100.0
    )
    _BLOCKSTATE_PROPS[7] = BlockStateProperties(
        block_id=7, is_air=False, is_solid=True, is_ladder=False, can_be_replaced=False, hardness=0.4
    )
    _BLOCKSTATE_PROPS[8] = BlockStateProperties(
        block_id=8, is_air=False, is_solid=True, is_soul_sand=True, can_be_replaced=False, hardness=0.5
    )
    _BLOCKSTATE_PROPS[9] = BlockStateProperties(
        block_id=9, is_air=False, is_solid=True, is_magma_block=True, can_be_replaced=False, hardness=0.5
    )
    _BLOCKSTATE_PROPS[10] = BlockStateProperties(
        block_id=10, is_air=False, is_solid=False, is_cactus=True, can_be_replaced=False, hardness=0.4
    )


init_default_blockstates()
