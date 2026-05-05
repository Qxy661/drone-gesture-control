# drone_landing

精准视觉降落 - ArUco 标记检测 + PnP 6DOF 位姿估计 + 级联 PID 控制

## 算法原理

```
ArUco Marker (地面)
        |
   相机检测 2D 角点
        |
   solvePnP -> 6DOF 位姿 (x, y, z, roll, pitch, yaw)
        |
   级联 PID 控制:
   - 水平位置误差 -> 水平速度命令
   - 水平速度误差 -> 倾斜角命令
   - 高度误差 -> 垂直速度命令
        |
   降落阶段状态机:
   COARSE -> FINE -> DESCENT -> FLARE -> LANDED
```

## Modules

| Module | File | 可独立使用 | 功能 |
|--------|------|-----------|------|
| ArUcoDetector | aruco_pose.py | Yes | ArUco 检测 + 多字典支持 |
| PnPPoseEstimator | aruco_pose.py | Yes | solvePnP 6DOF 位姿估计 |
| LandingDetector | landing_detector.py | No (ROS) | ROS2 节点: 检测+发布位姿 |
| LandingController | landing_controller.py | No (ROS) | 级联 PID 降落控制 |
| MissionPlanner | mission_planner.py | No (ROS) | 降落任务状态机 |

## Launch

```bash
# 测试模式 (用摄像头, 不连飞控)
ros2 launch drone_landing landing_test.launch.py

# 真机模式 (RTSP + MAVROS)
ros2 launch drone_landing landing_system.launch.py
```

## 测试

```bash
python3 src/drone_landing/test/test_aruco_pose.py
```

## 降落阶段

| 阶段 | 高度 | 水平精度 | 下降速度 | 说明 |
|------|------|---------|---------|------|
| COARSE | >3m | ±0.5m | - | 粗定位, 大幅修正 |
| FINE | 1-3m | ±0.2m | - | 精对准, 小幅修正 |
| DESCENT | 0.3-1m | ±0.1m | 0.3 m/s | 稳定下降 |
| FLARE | <0.3m | ±0.05m | 0.1 m/s | 缓冲着陆 |
| LANDED | 0 | - | 0 | 完成 |
