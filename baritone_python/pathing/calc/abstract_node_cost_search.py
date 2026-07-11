from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import time

from .path_node import PathNode
from .openset.binary_heap_open_set import BinaryHeapOpenSet
from .path import Path, PathCalculationResultType
from ..movement.calculation_context import CalculationContext
from ..movement.moves import Moves
from ...api.pathing.goals.goal import Goal
from ...api.utils.better_block_pos import BetterBlockPos
from ...utils.favoring import Favoring
from ..movement.action_costs import COST_INF
from ...settings import Settings
from ..movement.movement import MovementState

if TYPE_CHECKING:
    pass


class AbstractNodeCostSearch(ABC):
    COEFFICIENTS = [1.5, 2, 2.5, 3, 4, 5, 10]
    MIN_DIST_PATH = 5.0
    MIN_IMPROVEMENT = 0.01

    def __init__(
        self,
        real_start: BetterBlockPos,
        start_x: int,
        start_y: int,
        start_z: int,
        goal: Goal,
        favoring: Favoring,
        context: CalculationContext,
    ) -> None:
        self.real_start = real_start
        self.start_x = start_x
        self.start_y = start_y
        self.start_z = start_z
        self.goal = goal
        self.favoring = favoring
        self.context = context
        self.settings: Settings = context.settings

        self.start_node: PathNode | None = None
        self.goal_node: PathNode | None = None
        self.best_so_far: PathNode | None = None
        self.best_so_far_by_coefficient: list[PathNode | None] = []
        self.lowest_combined_cost_by_coefficient: list[float] = []
        self.num_nodes_considered = 0
        self.cancel_flag = False

        map_size = self.settings.pathing_map_default_size
        self._map: dict[int, PathNode] = {}

        self.open_set = BinaryHeapOpenSet(map_size)

    @abstractmethod
    def calculate(self, primary_timeout_ms: float, failure_timeout_ms: float) -> Path | None:
        ...

    def cancel(self) -> None:
        self.cancel_flag = True

    def get_node_at(self, x: int, y: int, z: int) -> PathNode:
        h = int(BetterBlockPos.long_hash(x, y, z))
        node = self._map.get(h)
        if node is None:
            node = PathNode(x, y, z, self.goal)
            self._map[h] = node
        return node

    def _favor(self, x: int, y: int, z: int, cost: float) -> float:
        if self.favoring.is_empty():
            return cost
        return cost * self.favoring.calculate(BetterBlockPos(x, y, z))

    def _get_dist_from_start_sq(self, node: PathNode) -> float:
        dx = node.x - self.start_x
        dy = node.y - self.start_y
        dz = node.z - self.start_z
        return dx * dx + dy * dy + dz * dz

    def _update_best(self, n: PathNode) -> None:
        for i, coeff in enumerate(self.COEFFICIENTS):
            cost_with_coeff = n.cost + n.estimated_cost_to_goal * coeff
            if cost_with_coeff < self.lowest_combined_cost_by_coefficient[i]:
                self.lowest_combined_cost_by_coefficient[i] = cost_with_coeff
                self.best_so_far_by_coefficient[i] = n
        if self.best_so_far is None or self._get_dist_from_start_sq(n) > self._get_dist_from_start_sq(self.best_so_far):
            self.best_so_far = n

    def _is_primary_timeout(self, start_time: float, timeout_ms: float) -> bool:
        if timeout_ms <= 0:
            return False
        return (time.time() * 1000 - start_time) > timeout_ms

    def _has_usable_path(self) -> bool:
        for i, coeff in enumerate(self.COEFFICIENTS):
            best_node = self.best_so_far_by_coefficient[i]
            if best_node is None:
                continue
            if self._get_dist_from_start_sq(best_node) < self.MIN_DIST_PATH * self.MIN_DIST_PATH:
                continue
            return True
        return False

    def _select_best(self) -> PathNode | None:
        for i, coeff in enumerate(self.COEFFICIENTS):
            best_node = self.best_so_far_by_coefficient[i]
            if best_node is None:
                continue
            if self._get_dist_from_start_sq(best_node) < self.MIN_DIST_PATH * self.MIN_DIST_PATH:
                continue
            return best_node
        return self.best_so_far

    def best_path_so_far(self) -> Path | None:
        if self.best_so_far is None or self.start_node is None:
            return None
        best = self._select_best()
        if best is None:
            return None
        return Path(self.real_start, self.start_node, best, self.num_nodes_considered)


class AStarPathFinder(AbstractNodeCostSearch):
    def __init__(
        self,
        real_start: BetterBlockPos,
        start_x: int,
        start_y: int,
        start_z: int,
        goal: Goal,
        favoring: Favoring,
        context: CalculationContext,
    ) -> None:
        super().__init__(real_start, start_x, start_y, start_z, goal, favoring, context)
        self.best_so_far_by_coefficient = [None] * len(self.COEFFICIENTS)
        self.lowest_combined_cost_by_coefficient = [COST_INF] * len(self.COEFFICIENTS)

    def calculate(self, primary_timeout_ms: float, failure_timeout_ms: float) -> Path | None:
        if self.cancel_flag:
            return None

        start_node = self.get_node_at(self.start_x, self.start_y, self.start_z)
        self.start_node = start_node
        start_node.cost = 0.0
        start_node.combined_cost = start_node.estimated_cost_to_goal
        start_node.previous = None
        self.open_set.insert(start_node)

        start_time = time.time() * 1000
        primary_timeout_hit = False
        path_to_goal_found = False
        last_improvement_time = start_time
        last_best_cost = COST_INF
        empty_chunk_check_budget = self.settings.pathing_max_chunk_border_fetch
        fetching_empties = empty_chunk_check_budget > 0

        moves_list = list(Moves)

        while not self.open_set.is_empty():
            if self.cancel_flag:
                return None

            current_time = time.time() * 1000

            if self._is_primary_timeout(start_time, primary_timeout_ms):
                primary_timeout_hit = True

            if primary_timeout_hit and path_to_goal_found:
                break

            if self._is_primary_timeout(start_time, failure_timeout_ms) and failure_timeout_ms > 0:
                break

            if self.settings.slow_path:
                slow_timeout = self.settings.slow_path_timeout_ms
                slow_delay = self.settings.slow_path_time_delay_ms
                if slow_timeout > 0 and (current_time - start_time) > slow_timeout:
                    break
                time.sleep(slow_delay / 1000.0)

            current = self.open_set.remove_lowest()
            self.num_nodes_considered += 1

            if self.goal.is_in_goal(current.x, current.y, current.z):
                self.goal_node = current
                path_to_goal_found = True
                if primary_timeout_hit:
                    break
                continue

            if current.cost < last_best_cost:
                last_best_cost = current.cost
                last_improvement_time = current_time
            elif current_time - last_improvement_time > 2000:
                if current.combined_cost - last_best_cost > self.MIN_IMPROVEMENT:
                    break

            x = current.x
            y = current.y
            z = current.z

            if fetching_empties:
                chunk_x = x >> 4
                chunk_z = z >> 4
                for dx in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        cx = chunk_x + dx
                        cz = chunk_z + dz
                        if not self.context.is_loaded(cx << 4, cz << 4):
                            empty_chunk_check_budget -= 1
                            if empty_chunk_check_budget < 0:
                                fetching_empties = False
                                break
                    if not fetching_empties:
                        break

            for move in moves_list:
                try:
                    state = MovementState()
                    movement = move.get_mover(self.context, x, y, z, state)
                    if movement.cost >= COST_INF:
                        continue

                    neighbor = self.get_node_at(movement.dest_x, movement.dest_y, movement.dest_z)

                    new_cost = current.cost + movement.cost
                    new_cost = self._favor(neighbor.x, neighbor.y, neighbor.z, new_cost)

                    if new_cost < neighbor.cost:
                        neighbor.cost = new_cost
                        neighbor.previous = current
                        neighbor.combined_cost = new_cost + neighbor.estimated_cost_to_goal

                        if neighbor.is_open():
                            self.open_set.update(neighbor)
                        else:
                            self.open_set.insert(neighbor)

                        self._update_best(neighbor)

                except Exception:
                    continue

        if self.goal_node is not None and self.start_node is not None:
            return Path(self.real_start, self.start_node, self.goal_node, self.num_nodes_considered)

        if self.best_so_far is not None and self.start_node is not None:
            best = self._select_best()
            if best is not None:
                return Path(self.real_start, self.start_node, best, self.num_nodes_considered)

        return None
