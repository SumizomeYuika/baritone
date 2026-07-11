from __future__ import annotations

from ...world.block_state_interface import BlockStateInterface
from ...world.block_state_provider import BlockStateProvider
from ...world.block_state import get_block_state_properties
from ...utils.tool_set import ToolSet
from .action_costs import COST_INF
from ...settings import Settings


class CalculationContext:
    def __init__(
        self,
        provider: BlockStateProvider,
        settings: Settings | None = None,
        tool_set: ToolSet | None = None,
    ) -> None:
        self.bsi = BlockStateInterface(provider)
        self.settings = settings or Settings()
        self.tool_set = tool_set or ToolSet()
        self.has_throwaway = True
        self.has_water_bucket = True
        self.can_sprint = True

    @property
    def world_border(self):
        return self.bsi.world_border

    def get(self, x: int, y: int, z: int) -> int:
        return self.bsi.get0(x, y, z)

    def get_block(self, x: int, y: int, z: int) -> int:
        state = self.get(x, y, z)
        return get_block_state_properties(state).block_id

    def is_loaded(self, x: int, z: int) -> bool:
        return self.bsi.is_loaded(x, z)

    @property
    def break_block_additional_cost(self) -> float:
        return self.settings.block_break_additional_penalty

    @property
    def place_block_cost(self) -> float:
        return self.settings.block_placement_penalty

    def cost_of_placing_at(self, x: int, y: int, z: int, state: int) -> float:
        if not self.settings.allow_place:
            return COST_INF
        if self.settings.allow_only_downward:
            return COST_INF
        props = get_block_state_properties(state)
        if props.is_liquid:
            return COST_INF
        return self.place_block_cost

    def break_cost_multiplier_at(self, x: int, y: int, z: int, state: int) -> float:
        if not self.settings.allow_break:
            if self.settings.allow_break_anyway:
                props = get_block_state_properties(state)
                if props.block_id in self.settings.allow_break_anyway:
                    return 1.0
            return COST_INF
        return 1.0

    def can_place(self, x: int, y: int, z: int) -> bool:
        if not self.settings.allow_place:
            return False
        if self.settings.allow_only_downward:
            return False
        return True
