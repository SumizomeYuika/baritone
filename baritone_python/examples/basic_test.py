#!/usr/bin/env python3
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from baritone_python import (
    SimpleWorldProvider,
    CalculationContext,
    AStarPathFinder,
    GoalBlock,
    BetterBlockPos,
    Favoring,
    Settings,
)


def test_straight_line():
    print("=== Test 1: Straight line path ===")
    world = SimpleWorldProvider(min_x=-10, max_x=10, min_y=0, max_y=10, min_z=-10, max_z=10)
    world.fill_floor(y=0)

    settings = Settings()
    settings.allow_break = True
    settings.allow_place = False
    settings.allow_parkour = False

    ctx = CalculationContext(world, settings=settings)
    goal = GoalBlock(5, 1, 0)
    favoring = Favoring()
    start = BetterBlockPos(0, 1, 0)

    finder = AStarPathFinder(start, 0, 1, 0, goal, favoring, ctx)
    result = finder.calculate(primary_timeout_ms=5000, failure_timeout_ms=10000)

    if result:
        print(f"Path found! Length: {result.length()}, Cost: {result.cost:.2f}")
        print(f"Nodes considered: {result.num_nodes_considered}")
        for i, pos in enumerate(result.positions()):
            print(f"  Step {i}: ({pos.x}, {pos.y}, {pos.z})")
        return True
    else:
        print("No path found!")
        return False


def test_around_obstacle():
    print("\n=== Test 2: Path around obstacle ===")
    world = SimpleWorldProvider(min_x=-10, max_x=10, min_y=0, max_y=10, min_z=-10, max_z=10)
    world.fill_floor(y=0)

    world.add_wall(2, 1, -2, 2, 2, 2)

    settings = Settings()
    settings.allow_break = False
    settings.allow_place = False
    settings.allow_parkour = False

    ctx = CalculationContext(world, settings=settings)
    goal = GoalBlock(5, 1, 0)
    favoring = Favoring()
    start = BetterBlockPos(0, 1, 0)

    finder = AStarPathFinder(start, 0, 1, 0, goal, favoring, ctx)
    result = finder.calculate(primary_timeout_ms=5000, failure_timeout_ms=10000)

    if result:
        print(f"Path found! Length: {result.length()}, Cost: {result.cost:.2f}")
        print(f"Nodes considered: {result.num_nodes_considered}")
        for i, pos in enumerate(result.positions()):
            print(f"  Step {i}: ({pos.x}, {pos.y}, {pos.z})")
        return True
    else:
        print("No path found!")
        return False


def test_goal_xz():
    print("\n=== Test 3: GoalXZ ===")
    world = SimpleWorldProvider(min_x=-10, max_x=10, min_y=0, max_y=10, min_z=-10, max_z=10)
    world.fill_floor(y=0)

    from baritone_python import GoalXZ

    settings = Settings()
    settings.allow_break = False
    settings.allow_place = False

    ctx = CalculationContext(world, settings=settings)
    goal = GoalXZ(5, 5)
    favoring = Favoring()
    start = BetterBlockPos(0, 1, 0)

    finder = AStarPathFinder(start, 0, 1, 0, goal, favoring, ctx)
    result = finder.calculate(primary_timeout_ms=5000, failure_timeout_ms=10000)

    if result:
        print(f"Path found! Length: {result.length()}, Cost: {result.cost:.2f}")
        print(f"Destination: ({result.get_dest().x}, {result.get_dest().y}, {result.get_dest().z})")
        return True
    else:
        print("No path found!")
        return False


if __name__ == "__main__":
    results = []
    results.append(test_straight_line())
    results.append(test_around_obstacle())
    results.append(test_goal_xz())

    print("\n=== Summary ===")
    passed = sum(1 for r in results if r)
    print(f"Passed: {passed}/{len(results)}")
    sys.exit(0 if all(results) else 1)
