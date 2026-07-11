from __future__ import annotations

from enum import Enum


class PathingBlockType(Enum):
    AIR = 0b00
    WATER = 0b01
    AVOID = 0b10
    SOLID = 0b11

    @property
    def bits(self) -> list[bool]:
        return [(self.value & 0b10) != 0, (self.value & 0b01) != 0]

    @staticmethod
    def from_bits(b1: bool, b2: bool) -> PathingBlockType:
        if b1:
            return PathingBlockType.SOLID if b2 else PathingBlockType.AVOID
        return PathingBlockType.WATER if b2 else PathingBlockType.AIR
