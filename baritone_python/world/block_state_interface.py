from .block_state_provider import BlockStateProvider


class BetterWorldBorder:
    def __init__(self, min_x: float, max_x: float, min_z: float, max_z: float) -> None:
        self.min_x = min_x
        self.max_x = max_x
        self.min_z = min_z
        self.max_z = max_z

    def entirely_contains(self, x: int, z: int) -> bool:
        return self.min_x <= x < self.max_x and self.min_z <= z < self.max_z

    def can_place_at(self, x: int, z: int) -> bool:
        return self.entirely_contains(x, z)


class BlockStateInterface:
    def __init__(self, provider: BlockStateProvider) -> None:
        self.provider = provider
        self.world_border = BetterWorldBorder(*provider.get_world_border())
        self._min_y = provider.dimension_min_y()
        self._height = provider.dimension_height()
        self._max_y = self._min_y + self._height
        self._prev_chunk = None
        self._prev_chunk_x = None
        self._prev_chunk_z = None

    def get0(self, x: int, y: int, z: int) -> int:
        if y < self._min_y or y >= self._max_y:
            return 0
        return self.provider.get_block_state(x, y, z)

    def is_loaded(self, x: int, z: int) -> bool:
        return self.provider.is_loaded(x, z)

    def world_contains_loaded_chunk(self, block_x: int, block_z: int) -> bool:
        return self.provider.is_loaded(block_x, block_z)
