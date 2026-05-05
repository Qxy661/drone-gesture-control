# drone_nav

自主导航与路径规划 — 航点飞行 + A*/RRT/DWA

## Modules

| Module | File | 可独立使用 | 功能 |
|--------|------|-----------|------|
| path_planner | path_planner.py | Yes | A*, RRT, RRT* 算法 |
| dwa_planner | dwa_planner.py | Yes | DWA 局部避障 |
| coordinate_utils | coordinate_utils.py | Yes | ENU/NED/GPS 坐标转换 |
| waypoint_navigator | waypoint_navigator.py | No (ROS) | MAVROS 航点导航 |
| mission_manager | mission_manager.py | No (ROS) | 任务编排状态机 |
| obstacle_map | obstacle_map.py | No (ROS) | 2D 栅格障碍物地图 |

## Launch

```bash
# 测试模式
ros2 launch drone_nav nav_test.launch.py

# 真机模式
ros2 launch drone_nav nav_system.launch.py
```

## 测试

```bash
python3 src/drone_nav/test/test_path_planner.py
python3 src/drone_nav/test/test_dwa.py
```
