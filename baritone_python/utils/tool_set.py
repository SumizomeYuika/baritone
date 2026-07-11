from __future__ import annotations

from ..world.block_state import get_block_state_properties


class ToolSet:
    def __init__(self) -> None:
        self.has_pickaxe = False
        self.has_axe = False
        self.has_shovel = False
        self.has_sword = False
        self.has_shears = False
        self.has_haste = False
        self.has_mining_fatigue = False

    def get_str_vs_block(self, blockstate_id: int) -> float:
        props = get_block_state_properties(blockstate_id)
        if props.is_air or props.hardness <= 0:
            return 0.0
        hardness = props.hardness
        base_speed = 1.0
        speed = base_speed / hardness
        return speed
