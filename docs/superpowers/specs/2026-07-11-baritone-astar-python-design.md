# Baritone A* Pathfinding - Python Conversion Design

## Overview

This document describes the design for converting the Baritone A* pathfinding algorithm from Java to Python. The goal is to create a faithful recreation of the original algorithm while making it idiomatic Python code.

## 1. Architecture

### 1.1 Package Structure

```
baritone_python/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── path_node.py
│   ├── binary_heap.py
│   ├── goal.py
│   └── a_star.py
├── movement/
│   ├── __init__.py
│   ├── moves.py
│   ├── movement.py
│   └── costs.py
├── world/
│   ├── __init__.py
│   ├── block_pos.py
│   ├── world.py
│   └── world_border.py
└── utils/
    ├── __init__.py
    ├── favoring.py
    └── math_utils.py
```

### 1.2 Component Relationships

```
AStarPathFinder
    ├── PathNode (nodes in search graph)
    ├── BinaryHeap (open set)
    ├── Goal (target condition)
    ├── Moves (movement options)
    ├── World (block data source)
    ├── WorldBorder (boundary checking)
    └── Favoring (cost modification)
```

## 2. Core Components

### 2.1 PathNode

**Location**: `core/path_node.py`

**Purpose**: Represents a node in the A* search graph, storing position, cost, and path information.

**Fields**:
- `x: int` - X coordinate
- `y: int` - Y coordinate  
- `z: int` - Z coordinate
- `estimated_cost_to_goal: float` - Heuristic estimate (cached)
- `cost: float` - Total cost from start to this node
- `combined_cost: float` - cost + estimated_cost_to_goal
- `previous: PathNode | None` - Previous node in path
- `heap_position: int` - Position in binary heap (-1 if not in heap)

**Methods**:
- `__init__(x, y, z, goal)` - Create node at position with heuristic from goal
- `is_open() -> bool` - Check if node is in open set
- `__hash__() -> int` - Hash based on position
- `__eq__(other) -> bool` - Compare by position

### 2.2 BinaryHeap

**Location**: `core/binary_heap.py`

**Purpose**: Min-heap implementation for the A* open set, supporting decrease-key operations.

**Fields**:
- `array: list[PathNode | None]` - Array backing the heap (1-based)
- `size: int` - Number of elements in heap

**Methods**:
- `__init__(initial_capacity=1024)` - Create heap with initial capacity
- `size() -> int` - Return number of elements
- `insert(node)` - Insert node into heap
- `update(node)` - Decrease-key operation (node cost decreased)
- `is_empty() -> bool` - Check if heap is empty
- `remove_lowest() -> PathNode` - Remove and return node with minimum combined_cost

### 2.3 Goal

**Location**: `core/goal.py`

**Purpose**: Abstract base class defining the target condition for pathfinding.

**Methods**:
- `is_in_goal(x: int, y: int, z: int) -> bool` - Check if position satisfies goal
- `heuristic(x: int, y: int, z: int) -> float` - Estimate cost to reach goal from position

**Concrete Implementations**:
- `GoalBlock(x, y, z)` - Goal is a specific block position
- `GoalXZ(x, z)` - Goal is any position at specific XZ coordinates
- `GoalYLevel(y)` - Goal is any position at specific Y level
- `GoalNear(x, y, z, radius)` - Goal is within radius of position

### 2.4 AStarPathFinder

**Location**: `core/a_star.py`

**Purpose**: Main A* pathfinding algorithm implementation.

**Fields**:
- `real_start: BlockPos` - Actual starting position
- `start_x: int`, `start_y: int`, `start_z: int` - Starting coordinates
- `goal: Goal` - Target goal
- `favoring: Favoring` - Cost modification system
- `world: World` - World data source

**Constants**:
- `COEFFICIENTS: tuple[float, ...]` - (1.5, 2, 2.5, 3, 4, 5, 10)
- `MIN_DIST_PATH: float` - 5.0
- `MIN_IMPROVEMENT: float` - 0.01

**Methods**:
- `__init__(real_start, start_x, start_y, start_z, goal, favoring, world)`
- `calculate(primary_timeout_ms, failure_timeout_ms) -> Path | None`
- `cancel()` - Request cancellation of ongoing calculation
- `best_path_so_far() -> Path | None` - Get best partial path

**Algorithm Flow**:
1. Initialize start node with cost 0
2. Insert start node into open set
3. While open set not empty:
   - Remove node with lowest combined_cost
   - If node is in goal, return path
   - For each movement type:
     - Calculate destination and cost
     - Skip if destination invalid or movement impossible
     - Update neighbor node if better path found
4. If timeout reached, return best path so far

## 3. Movement System

### 3.1 Moves

**Location**: `movement/moves.py`

**Purpose**: Enum of all possible movement types with direction offsets.

**Movement Types**:
- `DOWNWARD` - Move down 1 block
- `PILLAR` - Move up 1 block (place block below)
- `TRAVERSE_NORTH/SOUTH/EAST/WEST` - Move horizontally 1 block
- `ASCEND_NORTH/SOUTH/EAST/WEST` - Move up and horizontally (jump)
- `DESCEND_NORTH/SOUTH/EAST/WEST` - Move down and horizontally
- `DIAGONAL_NORTHEAST/NORTHWEST/SOUTHEAST/SOUTHWEST` - Move diagonally
- `PARKOUR_NORTH/SOUTH/EAST/WEST` - 4-block jump

**Fields per Movement**:
- `x_offset: int` - X distance moved
- `y_offset: int` - Y distance moved
- `z_offset: int` - Z distance moved
- `dynamic_xz: bool` - Whether XZ destination varies
- `dynamic_y: bool` - Whether Y destination varies

**Methods**:
- `apply(world, x, y, z) -> MoveResult` - Calculate destination and cost
- `cost(world, x, y, z) -> float` - Calculate movement cost

### 3.2 Movement

**Location**: `movement/movement.py`

**Purpose**: Represents an individual movement from one position to another.

**Fields**:
- `source: BlockPos` - Starting position
- `destination: BlockPos` - Ending position
- `cost: float` - Cost of this movement

**Methods**:
- `__init__(source, destination, cost)`
- `override(new_cost)` - Set a new cost for this movement

### 3.3 ActionCosts

**Location**: `movement/costs.py`

**Purpose**: Constants for movement costs.

**Constants**:
- `COST_INF: float` - Infinity (impossible movement)
- `COST_1: float` - 1.0 (normal walking)
- `COST_1_25: float` - 1.25 (slight penalty)
- `COST_2: float` - 2.0 (jumping)
- `COST_3: float` - 3.0 (pillar jump)
- `COST_4: float` - 4.0 (parkour)

## 4. World Representation

### 4.1 BlockPos

**Location**: `world/block_pos.py`

**Purpose**: Immutable 3D position with efficient hashing.

**Fields**:
- `x: int`
- `y: int`
- `z: int`

**Methods**:
- `__init__(x, y, z)`
- `__hash__() -> int` - Use long hash for dictionary keys
- `__eq__(other) -> bool`
- `above(n=1) -> BlockPos`
- `below(n=1) -> BlockPos`
- `north(n=1) -> BlockPos`
- `south(n=1) -> BlockPos`
- `east(n=1) -> BlockPos`
- `west(n=1) -> BlockPos`
- `distance_sq(other) -> float`
- `distance_to(other) -> float`

**Static Methods**:
- `long_hash(x, y, z) -> int` - Hash function from original BetterBlockPos

### 4.2 World

**Location**: `world/world.py`

**Purpose**: Dictionary-based world representation providing block data.

**Fields**:
- `blocks: dict[tuple[int, int, int], int]` - Block type at position
- `default_block: int` - Block type for positions not in dictionary
- `loaded_chunks: set[tuple[int, int]]` - Set of loaded chunk coordinates

**Methods**:
- `__init__(default_block=0)`
- `get_block(x, y, z) -> int` - Get block type at position
- `set_block(x, y, z, block_type)` - Set block type at position
- `is_loaded(x, z) -> bool` - Check if chunk containing position is loaded
- `load_chunk(chunk_x, chunk_z)` - Mark chunk as loaded
- `unload_chunk(chunk_x, chunk_z)` - Mark chunk as unloaded

### 4.3 WorldBorder

**Location**: `world/world_border.py`

**Purpose**: Check if positions are within the world border.

**Fields**:
- `min_x: float`, `max_x: float`
- `min_z: float`, `max_z: float`

**Methods**:
- `__init__(min_x, max_x, min_z, max_z)`
- `entirely_contains(x, z) -> bool` - Check if position is within border

## 5. Utility Components

### 5.1 Favoring

**Location**: `utils/favoring.py`

**Purpose**: System for modifying movement costs based on position.

**Fields**:
- `favors: dict[int, float]` - Hash -> multiplier mapping

**Methods**:
- `__init__()`
- `add_favor(hash_value, multiplier)` - Add cost multiplier for position
- `calculate(hash_value) -> float` - Get multiplier for position (1.0 if not found)
- `is_empty() -> bool` - Check if any favors are defined

### 5.2 MathUtils

**Location**: `utils/math_utils.py`

**Purpose**: Mathematical helper functions.

**Functions**:
- `get_dist_from_start_sq(node, start_x, start_y, start_z) -> float`
- `chunk_coord(x_or_z) -> int` - Convert block coordinate to chunk coordinate

## 6. Path Result

### 6.1 Path

**Location**: `core/a_star.py` (inner class or separate file)

**Purpose**: Represents a computed path from start to destination.

**Fields**:
- `start: BlockPos`
- `end: BlockPos`
- `positions: list[BlockPos]` - Ordered list of positions
- `nodes: list[PathNode]` - Ordered list of nodes
- `num_nodes_considered: int`

**Methods**:
- `__init__(real_start, start_node, end_node, num_nodes)`
- `length() -> int` - Number of positions in path
- `get_src() -> BlockPos`
- `get_dest() -> BlockPos`
- `reconstruct_path() -> list[BlockPos]` - Reconstruct path from nodes

## 7. Key Algorithm Features

### 7.1 Multi-coefficient Heuristic

The algorithm maintains multiple "best so far" paths using different cost coefficients:
- Each coefficient balances between exploration and exploitation
- Coefficients: [1.5, 2, 2.5, 3, 4, 5, 10]
- Lower coefficients = more greedy (focus on heuristic)
- Higher coefficients = more thorough (focus on actual cost)
- Returns first path that achieves minimum distance threshold

### 7.2 Favoring System

Allows biasing paths:
- Apply cost multiplier based on position hash
- Can favor certain areas (reduce cost) or avoid areas (increase cost)
- Useful for: avoiding water, preferring certain blocks, etc.

### 7.3 Timeout Handling

- **Primary timeout**: Stops when path to goal is found and timeout expires
- **Failure timeout**: Stops even without finding goal after extended search
- **Slow path mode**: Adds delays between iterations for debugging

### 7.4 Chunk Loading Awareness

- Checks if destination chunk is loaded before considering movement
- Prevents pathing into unloaded areas
- Configurable maximum empty chunks allowed

## 8. Testing

### 8.1 Unit Tests

- BinaryHeap insertion, removal, update operations
- PathNode hashing and equality
- Goal heuristic calculations
- Movement cost calculations
- World block lookups
- WorldBorder containment checks

### 8.2 Integration Tests

- Simple straight-line pathfinding
- Pathfinding around obstacles
- Multi-coefficient heuristic selection
- Timeout behavior with incomplete paths
- Favoring system cost modification

### 8.3 Benchmark Tests

- Nodes processed per second
- Memory usage for different world sizes
- Pathfinding time for various path lengths
- Comparison with Java version performance

## 9. Dependencies

- Python 3.10+ (for type hints and match statements)
- No external dependencies (pure Python implementation)

## 10. Usage Example

```python
from baritone_python import AStarPathFinder, GoalBlock, World, BlockPos

# Create a world
world = World()
world.set_block(0, 0, 1, 1)  # Place obstacle
world.set_block(0, 0, 2, 1)

# Create pathfinder
start = BlockPos(0, 0, 0)
goal = GoalBlock(0, 0, 5)
finder = AStarPathFinder(start, 0, 0, 0, goal, WorldBorder(-30000000, 30000000, -30000000, 30000000))

# Find path
path = finder.calculate(5000, 10000)
if path:
    print(f"Path found: {len(path.positions)} blocks")
    for pos in path.positions:
        print(pos)
else:
    print("No path found")
```