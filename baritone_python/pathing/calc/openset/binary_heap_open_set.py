from __future__ import annotations

from .i_open_set import IOpenSet
from ..path_node import PathNode

INITIAL_CAPACITY = 1024


class BinaryHeapOpenSet(IOpenSet):
    def __init__(self, size: int = INITIAL_CAPACITY) -> None:
        self._size = 0
        self._array: list[PathNode | None] = [None] * (size + 1)

    def size(self) -> int:
        return self._size

    def insert(self, value: PathNode) -> None:
        if self._size >= len(self._array) - 1:
            new_array = [None] * (len(self._array) * 2)
            for i in range(len(self._array)):
                new_array[i] = self._array[i]
            self._array = new_array
        self._size += 1
        value.heap_position = self._size
        self._array[self._size] = value
        self.update(value)

    def update(self, val: PathNode) -> None:
        index = val.heap_position
        parent_ind = index >> 1
        cost = val.combined_cost
        parent_node = self._array[parent_ind]
        while index > 1 and parent_node.combined_cost > cost:
            self._array[index] = parent_node
            self._array[parent_ind] = val
            val.heap_position = parent_ind
            parent_node.heap_position = index
            index = parent_ind
            parent_ind = index >> 1
            parent_node = self._array[parent_ind]

    def is_empty(self) -> bool:
        return self._size == 0

    def remove_lowest(self) -> PathNode:
        if self._size == 0:
            raise ValueError("Cannot remove from empty heap")
        result = self._array[1]
        val = self._array[self._size]
        self._array[1] = val
        val.heap_position = 1
        self._array[self._size] = None
        self._size -= 1
        result.heap_position = -1
        if self._size < 2:
            return result
        index = 1
        smaller_child = 2
        cost = val.combined_cost
        while True:
            smaller_child_node = self._array[smaller_child]
            smaller_child_cost = smaller_child_node.combined_cost
            if smaller_child < self._size:
                right_child_node = self._array[smaller_child + 1]
                right_child_cost = right_child_node.combined_cost
                if smaller_child_cost > right_child_cost:
                    smaller_child += 1
                    smaller_child_cost = right_child_cost
                    smaller_child_node = right_child_node
            if cost <= smaller_child_cost:
                break
            self._array[index] = smaller_child_node
            self._array[smaller_child] = val
            val.heap_position = smaller_child
            smaller_child_node.heap_position = index
            index = smaller_child
            smaller_child <<= 1
            if smaller_child > self._size:
                break
        return result
