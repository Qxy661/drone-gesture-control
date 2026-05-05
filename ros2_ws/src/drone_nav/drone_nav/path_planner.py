"""
路径规划算法库
Path Planning Algorithms

实现:
- AStarPlanner: A* 栅格搜索
- RRTPlanner: 快速随机树
- RRTStarPlanner: RRT* (带路径优化)

所有规划器在 2D 栅格地图上工作, 返回路径点列表 [(x,y), ...]
纯 Python 实现, 不依赖 ROS, 可独立使用
"""
import math
import random
import heapq
from typing import List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class GridMap:
    """2D 栅格地图
    0 = 可通行, 1 = 障碍物
    """
    width: int
    height: int
    resolution: float = 0.1  # 每格代表的米数
    data: list = field(default_factory=list)

    def __post_init__(self):
        if not self.data:
            self.data = [[0] * self.width for _ in range(self.height)]

    def set_obstacle(self, x: int, y: int):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.data[y][x] = 1

    def is_free(self, x: int, y: int) -> bool:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y][x] == 0
        return False

    def world_to_grid(self, wx: float, wy: float) -> Tuple[int, int]:
        return int(wx / self.resolution), int(wy / self.resolution)

    def grid_to_world(self, gx: int, gy: int) -> Tuple[float, float]:
        return gx * self.resolution, gy * self.resolution


class AStarPlanner:
    """A* 路径规划器

    A* = Dijkstra + 启发函数
    - f(n) = g(n) + h(n)
    - g(n): 从起点到当前节点的实际代价
    - h(n): 从当前节点到终点的估计代价 (启发式)
    - 保证最优解 (当 h 是可接受的)

    常用启发函数:
    - 欧氏距离: sqrt(dx^2 + dy^2) -- 8方向移动
    - 曼哈顿距离: |dx| + |dy| -- 4方向移动
    """
    # 8方向移动 (含对角线)
    DIRS_8 = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
    COSTS_8 = [1, 1, 1, 1, 1.414, 1.414, 1.414, 1.414]

    # 4方向移动
    DIRS_4 = [(0,1),(0,-1),(1,0),(-1,0)]

    def __init__(self, grid_map: GridMap, use_diagonal: bool = True):
        self.map = grid_map
        self.dirs = self.DIRS_8 if use_diagonal else self.DIRS_4
        self.costs = self.COSTS_8 if use_diagonal else [1,1,1,1]

    def plan(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """A* 搜索
        返回: 路径点列表 (栅格坐标), 或 None (无解)
        """
        sx, sy = start
        gx, gy = goal
        if not self.map.is_free(sx, sy) or not self.map.is_free(gx, gy):
            return None

        # 优先队列: (f_score, x, y)
        open_set = [(0, sx, sy)]
        came_from = {}
        g_score = {(sx, sy): 0}

        while open_set:
            _, cx, cy = heapq.heappop(open_set)

            if (cx, cy) == (gx, gy):
                return self._reconstruct(came_from, (cx, cy))

            for (dx, dy), cost in zip(self.dirs, self.costs):
                nx, ny = cx + dx, cy + dy
                if not self.map.is_free(nx, ny):
                    continue

                new_g = g_score[(cx, cy)] + cost
                if (nx, ny) not in g_score or new_g < g_score[(nx, ny)]:
                    g_score[(nx, ny)] = new_g
                    f = new_g + self._heuristic(nx, ny, gx, gy)
                    heapq.heappush(open_set, (f, nx, ny))
                    came_from[(nx, ny)] = (cx, cy)

        return None  # 无解

    def _heuristic(self, x1, y1, x2, y2):
        """欧氏距离启发函数"""
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def _reconstruct(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path


class RRTPlanner:
    """RRT 快速随机树规划器

    RRT 原理:
    1. 从起点开始生长一棵随机树
    2. 每次随机采样一个点
    3. 从树上最近的节点向采样点扩展一步 (step_size)
    4. 如果扩展的路径无障碍, 将新节点加入树
    5. 重复直到新节点足够接近目标

    特点: 快速找到可行解, 但路径不一定最优
    """
    def __init__(self, grid_map: GridMap, step_size: float = 0.5,
                 goal_bias: float = 0.1, max_iter: int = 5000):
        self.map = grid_map
        self.step_size = step_size  # 每步扩展距离 (米)
        self.goal_bias = goal_bias  # 朝目标采样的概率
        self.max_iter = max_iter
        self.nodes = []  # [(x, y, parent_idx), ...]

    def plan(self, start: Tuple[float, float],
             goal: Tuple[float, float]) -> Optional[List[Tuple[float, float]]]:
        """RRT 搜索
        start, goal: 世界坐标 (米)
        返回: 路径点列表 (世界坐标), 或 None
        """
        self.nodes = [(start[0], start[1], -1)]

        for i in range(self.max_iter):
            # 采样: goal_bias 概率朝目标, 否则随机
            if random.random() < self.goal_bias:
                rx, ry = goal
            else:
                rx = random.uniform(0, self.map.width * self.map.resolution)
                ry = random.uniform(0, self.map.height * self.map.resolution)

            # 找最近节点
            nearest_idx = self._nearest(rx, ry)
            nx, ny, _ = self.nodes[nearest_idx]

            # 向采样点扩展一步
            dx, dy = rx - nx, ry - ny
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 1e-6:
                continue
            step = min(self.step_size, dist)
            sx = nx + dx / dist * step
            sy = ny + dy / dist * step

            # 检查路径是否无碰撞
            if not self._collision_free(nx, ny, sx, sy):
                continue

            # 加入新节点
            self.nodes.append((sx, sy, nearest_idx))

            # 检查是否到达目标
            if math.sqrt((sx - goal[0])**2 + (sy - goal[1])**2) < self.step_size:
                self.nodes.append((goal[0], goal[1], len(self.nodes) - 1))
                return self._reconstruct(len(self.nodes) - 1)

        return None  # 超过最大迭代

    def _nearest(self, x, y):
        best_i, best_d = 0, float('inf')
        for i, (nx, ny, _) in enumerate(self.nodes):
            d = (nx - x)**2 + (ny - y)**2
            if d < best_d:
                best_d = d
                best_i = i
        return best_i

    def _collision_free(self, x1, y1, x2, y2) -> bool:
        """线段碰撞检测 (Bresenham)"""
        gx1, gy1 = self.map.world_to_grid(x1, y1)
        gx2, gy2 = self.map.world_to_grid(x2, y2)
        # 简单采样检测
        steps = max(abs(gx2 - gx1), abs(gy2 - gy1), 1)
        for i in range(steps + 1):
            t = i / steps
            gx = int(gx1 + t * (gx2 - gx1))
            gy = int(gy1 + t * (gy2 - gy1))
            if not self.map.is_free(gx, gy):
                return False
        return True

    def _reconstruct(self, idx):
        path = []
        while idx != -1:
            x, y, idx = self.nodes[idx]
            path.append((x, y))
        path.reverse()
        return path


class RRTStarPlanner(RRTPlanner):
    """RRT* 规划器 (在 RRT 基础上增加路径优化)

    RRT* 改进:
    - 新节点加入时, 选择使总代价最小的父节点 (choose_parent)
    - 加入后尝试重连周围节点 (rewire), 使路径更短
    - 渐近最优: 随着迭代增加, 路径趋近最优解
    """
    def __init__(self, grid_map: GridMap, step_size=0.5, goal_bias=0.1,
                 max_iter=5000, rewire_radius: float = 1.0):
        super().__init__(grid_map, step_size, goal_bias, max_iter)
        self.rewire_radius = rewire_radius

    def plan(self, start, goal):
        self.nodes = [(start[0], start[1], -1)]
        self.costs = [0.0]  # 每个节点的累计代价

        for i in range(self.max_iter):
            if random.random() < self.goal_bias:
                rx, ry = goal
            else:
                rx = random.uniform(0, self.map.width * self.map.resolution)
                ry = random.uniform(0, self.map.height * self.map.resolution)

            nearest_idx = self._nearest(rx, ry)
            nx, ny, _ = self.nodes[nearest_idx]

            dx, dy = rx - nx, ry - ny
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 1e-6:
                continue
            step = min(self.step_size, dist)
            sx = nx + dx / dist * step
            sy = ny + dy / dist * step

            if not self._collision_free(nx, ny, sx, sy):
                continue

            # choose_parent: 找周围节点中使代价最小的
            best_parent = nearest_idx
            best_cost = self.costs[nearest_idx] + math.sqrt((sx-nx)**2 + (sy-ny)**2)
            for j, (px, py, _) in enumerate(self.nodes):
                if j == nearest_idx:
                    continue
                d = math.sqrt((sx-px)**2 + (sy-py)**2)
                if d < self.rewire_radius and self._collision_free(px, py, sx, sy):
                    c = self.costs[j] + d
                    if c < best_cost:
                        best_cost = c
                        best_parent = j

            new_idx = len(self.nodes)
            self.nodes.append((sx, sy, best_parent))
            self.costs.append(best_cost)

            # rewire: 尝试通过新节点优化周围节点
            for j, (px, py, _) in enumerate(self.nodes):
                if j == best_parent or j >= new_idx:
                    continue
                d = math.sqrt((sx-px)**2 + (sy-py)**2)
                if d < self.rewire_radius:
                    new_cost = best_cost + d
                    if new_cost < self.costs[j] and self._collision_free(sx, sy, px, py):
                        self.nodes[j] = (px, py, new_idx)
                        self.costs[j] = new_cost

            if math.sqrt((sx - goal[0])**2 + (sy - goal[1])**2) < self.step_size:
                goal_idx = len(self.nodes)
                self.nodes.append((goal[0], goal[1], new_idx))
                self.costs.append(best_cost + math.sqrt((sx-goal[0])**2 + (sy-goal[1])**2))
                return self._reconstruct(goal_idx)

        return None
