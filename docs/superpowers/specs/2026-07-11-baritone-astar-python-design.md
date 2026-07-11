# Baritone A* Pathfinding - Python Conversion Design

## Overview

This document describes the design for converting the Baritone A* pathfinding algorithm from Java to Python. The goal is to create a **faithful recreation** of the original algorithm with identical behavior, using the same movement cost calculations, block property logic, and heuristic system as the original Baritone mod.

## 1. Architecture

### 1.1 Package Structure

```
baritone_python/
├── __init__.py
├── api/                          # Public API (mirrors baritone.api)
│   ├── __init__.py
│   ├── pathing/
│   │   ├── __init__.py
│   │   ├── calc/
│   │   │   ├── __init__.py
│   │   │   ├── ipath.py          # IPath interface
│   │   │   └── ipath_finder.py   # IPathFinder interface
│   │   ├── goals/
│   │   │   ├── __init__.py
│   │   │   └── goal.py           # Goal base class
│   │   └── movement/
│   │       ├── __init__.py
│   │       ├── action_costs.py   # ActionCosts constants
│   │       └── imovement.py      # IMovement interface
│   └── utils/
│       ├── __init__.py
│       └── better_block_pos.py   # BetterBlockPos
├── pathing/                      # Core pathing implementation
│   ├── __init__.py
│   ├── calc/
│   │   ├── __init__.py
│   │   ├── path_node.py          # PathNode
│   │   ├── path.py               # Path
│   │   ├── abstract_node_cost_search.py  # AbstractNodeCostSearch
│   │   ├── a_star_path_finder.py # AStarPathFinder
│   │   └── openset/
│   │       ├── __init__.py
│   │       ├── i_open_set.py     # IOpenSet interface
│   │       └── binary_heap_open_set.py  # BinaryHeapOpenSet
│   └── movement/
│       ├── __init__.py
│       ├── calculation_context.py # CalculationContext
│       ├── movement_helper.py    # MovementHelper (static helpers)
│       ├── movement.py           # Movement base class
│       ├── moves.py              # Moves enum (all movement types)
│       ├── movement_state.py     # MovementState
│       └── movements/            # Individual movement implementations
│           ├── __init__.py
│           ├── movement_traverse.py
│           ├── movement_ascend.py
│           ├── movement_descend.py
│           ├── movement_downward.py
│           ├── movement_pillar.py
│           ├── movement_diagonal.py
│           ├── movement_fall.py
│           └── movement_parkour.py
├── world/                        # World data access
│   ├── __init__.py
│   ├── block_state_interface.py  # BlockStateInterface (核心数据访问层)
│   ├── world_border.py           # BetterWorldBorder
│   ├── block_state_provider.py   # Abstract base for block state providers
│   └── block_state.py            # BlockState properties
├── utils/
│   ├── __init__.py
│   ├── favoring.py               # Favoring
│   ├── tool_set.py               # ToolSet
│   └── math_utils.py             # Math helpers
└── settings.py                   # Settings (pathing config options)
```

### 1.2 Component Relationships (Data Flow)

```
AStarPathFinder
    ├── CalculationContext (寻路计算上下文)
    │   ├── BlockStateInterface (方块状态访问 → 你的 bot API)
    │   ├── WorldBorder (世界边界)
    │   ├── ToolSet (工具信息)
    │   ├── Favoring (路径偏好)
    │   └── Settings (各种配置)
    ├── PathNode (搜索图节点)
    ├── BinaryHeapOpenSet (开放集合)
    ├── Goal (目标条件)
    └── Moves (所有移动类型枚举)
        └── Movement*.cost() (每种移动的代价计算)
            └── MovementHelper (静态判断函数)
                └── BlockStateInterface.get0(x,y,z) (查询方块)
```

## 2. 核心接口：你的 bot 需要提供什么

### 2.1 BlockStateProvider (你的 bot 实现这个)

这是 Python 版寻路算法与外部世界交互的**唯一接口**。你的 bot 只需要实现这个抽象基类：

```python
from abc import ABC, abstractmethod

class BlockStateProvider(ABC):
    """
    方块状态提供者接口。
    你的 bot 需要实现这个接口来为寻路算法提供世界数据。
    设计对应原版 Baritone 的 BlockStateInterface。
    """
    
    @abstractmethod
    def get_block_state(self, x: int, y: int, z: int) -> int:
        """
        获取指定位置的方块状态 ID (blockstate id)。
        对于未加载的区域，返回空气方块的 ID。
        
        对应原版: BlockStateInterface.get0(x, y, z)
        """
        ...
    
    @abstractmethod
    def is_loaded(self, x: int, z: int) -> bool:
        """
        检查指定方块位置所在的区块是否已加载。
        
        对应原版: BlockStateInterface.isLoaded(x, z)
        """
        ...
    
    @abstractmethod
    def get_world_border(self) -> tuple[float, float, float, float]:
        """
        获取世界边界。
        返回: (min_x, max_x, min_z, max_z)
        """
        ...
    
    @abstractmethod
    def dimension_min_y(self) -> int:
        """
        获取当前维度的最低 Y 坐标。
        主世界: -64, 下界: 0, 末地: 0
        """
        ...
    
    @abstractmethod
    def dimension_height(self) -> int:
        """
        获取当前维度的高度。
        主世界: 384 (从 -64 到 320)
        """
        ...
```

### 2.2 为什么用 blockstate id 而不是方块类型？

因为 Baritone 的移动代价计算依赖于**非常细致**的方块属性判断，例如：

- 这个方块是普通固体方块吗？（`isBlockNormalCube`）
- 是台阶吗？是上半还是下半？（`SlabBlock.TYPE`）
- 是楼梯吗？朝向哪里？（`StairBlock.FACING`, `StairBlock.HALF`）
- 是门吗？开着还是关着？（`DoorBlock.OPEN`）
- 是雪层吗？几层？（`SnowLayerBlock.LAYERS`）
- 是水吗？静止的还是流动的？（`LiquidBlock.LEVEL`）

完整的 blockstate id 可以唯一确定所有这些属性。Python 版本会**内置一张 blockstate id → 属性的映射表**，这样计算逻辑就和原版完全一致了。

## 3. 方块属性系统 (BlockState)

### 3.1 设计思路

Baritone 并不直接使用 `BlockState` 的所有属性，而是通过一系列辅助函数来判断方块的行为属性。我们在 Python 中复刻这些判断函数：

### 3.2 核心判断函数 (MovementHelper)

所有这些函数的逻辑都与原版 Baritone 完全一致：

| 函数 | 作用 | 原版对应 |
|---|---|---|
| `can_walk_through(bsi, x, y, z, state)` | 能不能穿过这个方块 | `MovementHelper.canWalkThrough` |
| `can_walk_on(bsi, x, y, z, state)` | 能不能站在这个方块上 | `MovementHelper.canWalkOn` |
| `fully_passable(bsi, x, y, z, state)` | 完全可通行（无减速） | `MovementHelper.fullyPassable` |
| `is_replaceable(x, y, z, state, bsi)` | 能不能在这个位置放方块 | `MovementHelper.isReplaceable` |
| `can_place_against(bsi, x, y, z, state)` | 能不能对着这个方块放方块 | `MovementHelper.canPlaceAgainst` |
| `get_mining_duration_ticks(ctx, x, y, z, state, include_falling)` | 挖掉这个方块要多久 | `MovementHelper.getMiningDurationTicks` |
| `avoid_breaking(bsi, x, y, z, state)` | 应不应该避免挖这个方块 | `MovementHelper.avoidBreaking` |
| `is_water(state)` | 是不是水 | `MovementHelper.isWater` |
| `is_lava(state)` | 是不是岩浆 | `MovementHelper.isLava` |
| `is_block_normal_cube(state)` | 是不是完整固体方块 | `MovementHelper.isBlockNormalCube` |

### 3.3 BlockState 属性表

我们内置一个 `blockstate_id -> BlockStateProperties` 的映射表：

```python
@dataclass
class BlockStateProperties:
    block_id: int                    # 方块类型 ID
    is_air: bool                     # 是空气
    is_solid: bool                   # 是固体（完整碰撞箱）
    is_water: bool                   # 是水
    is_lava: bool                    # 是岩浆
    is_liquid: bool                  # 是液体
    water_level: int | None          # 水的等级 (0-8，None 表示不是水)
    is_slab: bool                    # 是台阶
    slab_type: str | None            # "bottom", "top", "double"
    is_stairs: bool                  # 是楼梯
    stair_half: str | None           # "bottom", "top"
    is_door: bool                    # 是门
    is_door_open: bool               # 门是否开着
    is_iron_door: bool               # 是铁门（不能手动开）
    is_fence_gate: bool              # 是栅栏门
    is_fence_gate_open: bool         # 栅栏门是否开着
    is_ladder: bool                  # 是梯子
    is_vine: bool                    # 是藤蔓
    is_snow: bool                    # 是雪层
    snow_layers: int | None          # 雪层厚度 (1-8)
    is_soul_sand: bool               # 是灵魂沙
    is_magma_block: bool             # 是岩浆块
    is_cactus: bool                  # 是仙人掌
    is_falling_block: bool           # 是受重力影响的方块（沙子、沙砾）
    is_fire: bool                    # 是火
    is_cobweb: bool                  # 是蜘蛛网
    is_end_portal: bool              # 是末地传送门
    is_honey_block: bool             # 是蜂蜜块
    is_bubble_column: bool           # 是气泡柱
    is_ice: bool                     # 是冰
    is_infested: bool                # 是虫蚀方块
    can_be_replaced: bool            # 可以被替换（放方块时直接覆盖）
    hardness: float                  # 硬度（用于计算挖掘时间）
```

### 3.4 为什么不全部内置？

完整的 Minecraft 有超过 1000 种 blockstate。我们有两种策略：

1. **完整内置**：把所有方块属性都内置到 Python 里
2. **按需查询**：你的 bot 提供属性查询 API，Python 版本缓存结果

考虑到性能和一致性，**推荐方案 1（完整内置）**，因为：
- 寻路时会大量重复查询相同方块
- 内置属性表查询是 O(1) 的
- 保证和原版逻辑完全一致

## 4. 计算上下文 (CalculationContext)

对应原版 `CalculationContext`，这是寻路计算时的"环境"：

```python
class CalculationContext:
    # 世界数据
    bsi: BlockStateInterface        # 方块状态访问
    world_border: BetterWorldBorder # 世界边界
    
    # 玩家能力/物品
    tool_set: ToolSet               # 工具集合（影响挖掘速度）
    has_water_bucket: bool          # 有没有水桶
    has_throwaway: bool             # 有没有可放置的方块
    can_sprint: bool                # 能不能冲刺
    
    # 移动能力开关
    allow_break: bool               # 允许破坏方块
    allow_break_anyway: list[int]   # 即使关闭 allow_break 也允许挖的方块
    allow_parkour: bool             # 允许跑酷跳
    allow_parkour_place: bool       # 跑酷时允许放方块
    allow_diagonal_descend: bool    # 允许斜向下走
    allow_diagonal_ascend: bool     # 允许斜向上走
    allow_downward: bool            # 允许向下挖
    assume_walk_on_water: bool      # 假设可以在水上走（Jesus 模组）
    frost_walker: int               # 冰霜行者等级 (0, 1, 2)
    
    # 代价系数
    place_block_cost: float         # 放方块的代价
    break_block_additional_cost: float  # 挖方块的额外代价
    water_walk_speed: float         # 水中行走速度
    walk_on_water_one_penalty: float   # 在水上走的惩罚
    backtrack_cost_favoring_coefficient: float
    jump_penalty: float
    
    # 下落相关
    min_fall_height: int
    max_fall_height_no_water: int
    max_fall_height_bucket: int
    
    # 方法
    def get(self, x, y, z) -> int:          # 获取方块状态 ID
    def is_loaded(self, x, z) -> bool:      # 检查是否已加载
    def get_block(self, x, y, z) -> int:    # 获取方块类型 ID
    def cost_of_placing_at(self, x, y, z, state) -> float:
    def break_cost_multiplier_at(self, x, y, z, state) -> float:
```

## 5. 核心算法组件

### 5.1 PathNode

**位置**: `pathing/calc/path_node.py`

和原版完全一致的字段：

```python
class PathNode:
    x: int
    y: int
    z: int
    estimated_cost_to_goal: float   # 到目标的启发式估值（缓存）
    cost: float                      # 从起点到这里的实际代价
    combined_cost: float             # cost + estimated_cost_to_goal
    previous: PathNode | None        # 路径上的前一个节点
    heap_position: int               # 在二叉堆中的位置 (-1 = 不在堆中)
```

### 5.2 BinaryHeapOpenSet

**位置**: `pathing/calc/openset/binary_heap_open_set.py`

完全复刻原版的二叉堆实现，使用 1-based 数组索引，支持 decrease-key。

### 5.3 AStarPathFinder + AbstractNodeCostSearch

**位置**: `pathing/calc/a_star_path_finder.py`, `pathing/calc/abstract_node_cost_search.py`

算法逻辑与原版逐行对应：
- 多系数启发式搜索（`COEFFICIENTS = [1.5, 2, 2.5, 3, 4, 5, 10]`）
- 主超时 + 失败超时的双重超时机制
- 分块加载检查（`pathingMaxChunkBorderFetch`）
- 最小改进阈值（`MIN_IMPROVEMENT = 0.01`）
- 最短路径距离阈值（`MIN_DIST_PATH = 5`）

### 5.4 Goal 系统

**位置**: `api/pathing/goals/goal.py`

复刻原版所有 Goal 类型：

| Goal 类型 | 作用 |
|---|---|
| `GoalBlock` | 到达具体方块 |
| `GoalXZ` | 到达指定 XZ 坐标（任意 Y） |
| `GoalYLevel` | 到达指定 Y 高度 |
| `GoalNear` | 到达目标附近一定范围内 |
| `GoalAxis` | 沿某条轴前进 |
| `GoalGetToBlock` | 站在/挨着某个方块 |
| `GoalStrictDirection` | 严格沿某个方向前进 |
| `GoalTwoBlocks` | 到达两格高的空间 |
| `GoalInverted` | 远离目标 |
| `GoalRunAway` | 逃离目标一定距离 |
| `GoalComposite` | 组合多个目标 |

## 6. 移动系统 (Movement)

### 6.1 所有移动类型

复刻原版全部 20 种移动：

| 类别 | 移动类型 | 数量 |
|---|---|---|
| 垂直移动 | DOWNWARD, PILLAR | 2 |
| 水平移动 | TRAVERSE_N/S/E/W | 4 |
| 上台阶 | ASCEND_N/S/E/W | 4 |
| 下台阶/下落 | DESCEND_N/S/E/W | 4 |
| 斜向移动 | DIAGONAL_NE/NW/SE/SW | 4 |
| 跑酷跳跃 | PARKOUR_N/S/E/W | 4 |
| 自由下落 | MovementFall | 1 |

**总计**: 23 种移动（含 MovementFall）

### 6.2 每种移动的代价计算

每种移动都有一个静态 `cost()` 方法，逻辑与原版完全一致。以 `MovementTraverse.cost()` 为例，它会：

1. 检查目的地脚下有没有方块（走路 vs 搭桥）
2. 检查身体和头部位置能不能通过
3. 计算需要挖掉的方块的代价
4. 如果是搭桥，计算放方块的代价和放置可行性
5. 考虑水、灵魂沙、岩浆块等特殊方块的影响
6. 考虑是否可以冲刺

### 6.3 Moves 枚举

对应原版 `Moves` 枚举，包含所有移动类型及其方向偏移量。

## 7. 工具与装备系统 (ToolSet)

影响挖掘速度，进而影响移动代价：

```python
class ToolSet:
    """
    复刻原版 ToolSet，根据玩家背包中的工具计算挖掘速度。
    你的 bot 提供玩家的物品栏信息。
    """
    def get_str_vs_block(self, block_state_id: int) -> float:
        """计算对指定方块的挖掘速度"""
        ...
```

## 8. 完整调用流程

```python
# 1. 你的 bot 实现 BlockStateProvider
class MyBotWorldProvider(BlockStateProvider):
    def get_block_state(self, x, y, z):
        return self.bot.get_blockstate(x, y, z)
    # ... 其他方法

# 2. 创建设置
settings = BaritoneSettings()
settings.allow_break = True
settings.allow_place = True
settings.allow_parkour = True
# ... 更多设置

# 3. 创建计算上下文
ctx = CalculationContext(
    world_provider=MyBotWorldProvider(...),
    tool_set=ToolSet(...),
    settings=settings,
    # ... 其他参数
)

# 4. 创建目标
goal = GoalBlock(100, 64, 200)

# 5. 创建寻路器
start = BetterBlockPos(0, 64, 0)
finder = AStarPathFinder(
    real_start=start,
    start_x=0, start_y=64, start_z=0,
    goal=goal,
    favoring=Favoring(),
    context=ctx
)

# 6. 开始寻路
result = finder.calculate(primary_timeout_ms=5000, failure_timeout_ms=10000)

# 7. 结果
if result.type == PathCalculationResultType.SUCCESS_TO_GOAL:
    path = result.path
    print(f"找到路径，长度 {len(path.positions())}")
```

## 9. 你的 bot 需要提供的数据汇总

### 9.1 必需的 API

| API | 用途 | 调用频率 |
|---|---|---|
| `get_block_state(x, y, z) -> int` | 获取方块状态 ID | **极高**（每次寻路可能调用数十万次） |
| `is_loaded(x, z) -> bool` | 检查区块是否加载 | 高 |
| `get_world_border() -> tuple` | 获取世界边界 | 低（初始化一次） |
| `dimension_min_y() -> int` | 维度最低 Y | 低 |
| `dimension_height() -> int` | 维度高度 | 低 |

### 9.2 可选的 API（用于更精确的代价计算）

| API | 用途 |
|---|---|
| `get_inventory() -> list[ItemStack]` | 获取玩家物品栏（用于工具速度、水桶、方块检测） |
| `get_food_level() -> int` | 饥饿值（影响能否冲刺） |
| `get_equipment_enchants() -> dict` | 装备附魔（冰霜行者等） |

### 9.3 性能建议

由于 `get_block_state` 调用频率极高，强烈建议：

1. **批量缓存**：你的 bot 可以一次性把周围若干区块的数据发给 Python 版本
2. **本地缓存**：Python 版本内部也会有缓存（对应原版的 `prev` 和 `prevCached` 优化）
3. **协议优化**：如果 bot 和 Python 版本通过网络通信，考虑用二进制协议

## 10. 设置选项 (Settings)

复刻原版所有影响寻路的设置：

```
allowBreak                    是否允许破坏方块
allowPlace                    是否允许放置方块
allowParkour                  是否允许跑酷
allowParkourPlace             跑酷时是否允许放方块
allowDiagonalDescend          是否允许斜向下
allowDiagonalAscend           是否允许斜向上
allowDownward                 是否允许向下挖
allowWaterBucketFall          是否允许用水桶落地
allowVines                    是否允许爬藤蔓
allowWalkOnMagmaBlocks        是否允许在岩浆块上走
assumeWalkOnWater             假设可以在水上走
assumeWalkOnLava              假设可以在岩浆上走
blockPlacementPenalty         放方块惩罚
blockBreakAdditionalPenalty   挖方块额外惩罚
maxFallHeightNoWater          无水下落最大高度
maxFallHeightBucket           用水桶下落最大高度
backtrackCostFavoringCoefficient  回溯代价偏好系数
jumpPenalty                   跳跃惩罚
walkOnWaterOnePenalty         在水上走的惩罚
pathingMapDefaultSize         路径节点映射默认大小
pathingMapLoadFactor          路径节点映射负载因子
pathingMaxChunkBorderFetch    最大空区块获取数
minimumImprovementRepropagation   最小改进重新传播
slowPath                      慢速寻路模式
slowPathTimeoutMS             慢速寻路超时
slowPathTimeDelayMS           慢速寻路延迟
... 等等
```

## 11. 测试

### 11.1 单元测试
- BinaryHeap 操作正确性
- PathNode 哈希和相等性
- Goal 启发式计算
- BlockState 属性判断（canWalkOn, canWalkThrough 等）
- 各 Movement 的代价计算边界情况

### 11.2 集成测试
- 简单直线路径
- 绕开障碍物的路径
- 上下台阶路径
- 搭桥路径（需要放置方块）
- 多系数启发式选择逻辑
- 超时行为

### 11.3 一致性测试（最重要）
- 使用相同的世界数据，对比 Python 版和 Java 版的输出
- 确保路径代价一致
- 确保节点扩展顺序一致（或等效）

## 12. 依赖

- Python 3.10+
- 无外部依赖（纯 Python 实现）
- 你的 bot 提供的 `BlockStateProvider` 实现

---

**设计核心原则**：算法逻辑 100% 对齐原版 Baritone，只在世界数据获取层做抽象，让你的 bot 通过 `BlockStateProvider` 接口接入。
