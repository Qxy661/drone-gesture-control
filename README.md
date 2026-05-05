\
# Drone Autonomy Suite

基于 ROS2 Humble 的无人机自主飞行系统，包含三个子项目：手势识别控制、自主导航路径规划、视觉目标跟踪。

## 系统架构

```
                        ┌─────────────────────────────────┐
                        │        Jetson Nano / PC          │
                        │         ROS2 Humble              │
                        │                                  │
  Camera/RTSP ─────────►│  ┌──────────────┐               │
                        │  │drone_gesture  │               │
  MediaPipe Hands       │  │手势识别+控制   │               │
                        │  └──────┬───────┘               │
                        │         │ /gesture               │
                        │  ┌──────▼───────┐  ┌──────────┐ │
                        │  │drone_nav     │  │drone_vision│ │
                        │  │自主导航+规划   │  │视觉跟踪    │ │
                        │  └──────┬───────┘  └─────┬────┘ │
                        │         │                 │      │
                        └─────────┼─────────────────┼──────┘
                                  │                 │
                           MAVROS │                 │
                                  │                 │
                        ┌─────────▼─────────────────▼──────┐
                        │         飞控 (V5+ / Pixhawk)      │
                        │          ArduCopter / PX4         │
                        └──────────────────────────────────┘
```

## 子项目

### 1. drone_gesture — 手势识别控制

通过 MediaPipe Hands 识别手势，映射为无人机控制命令。

| 手势 | 动作 | 实现 |
|------|------|------|
| 张开手掌 | 起飞 | Arm + GUIDED + takeoff |
| 握拳 | 降落 | LAND mode |
| 竖拇指 | 前进 | velocity setpoint |
| OK手势 | 功能键 | 自定义命令 |

**节点:**
- `gesture_recognizer` — MediaPipe 手势识别，发布到 /gesture
- `gesture_commander` — 手势→MAVLink 命令映射，状态机控制
- `safety_monitor` — 电量/连接/心跳监控，自动紧急降落
- `diagnostics` — 系统诊断聚合，CPU/内存/FPS 监控

### 2. drone_nav — 自主导航与路径规划

航点飞行 + A*/RRT 路径规划 + 坐标系转换。

**核心模块:**
- `path_planner.py` — A*、RRT、RRT* 算法实现（纯Python，可独立使用）
- `coordinate_utils.py` — ENU/NED/Body/GPS 坐标转换
- `waypoint_navigator.py` — MAVROS 航点导航
- `mission_manager.py` — 任务编排状态机
- `obstacle_map.py` — 2D 栅格障碍物地图

### 3. drone_vision — 视觉目标跟踪

目标检测 + 视觉伺服控制，实现无人机跟随地面目标。

**核心模块:**
- `target_detector.py` — OpenCV 目标检测（颜色/ArUco/模板匹配）
- `visual_servo.py` — PID 视觉伺服控制器（CENTER/FOLLOW/CIRCLE模式）
- `camera_model.py` — 针孔相机模型、像素-3D投影（纯Python，可独立使用）
- `tracking_manager.py` — 跟踪任务编排

## 快速开始

### 环境要求

- Ubuntu 22.04 / WSL2
- ROS2 Humble
- Python 3.10+

### 安装依赖

```bash
# ROS2 依赖
sudo apt install ros-humble-mavros ros-humble-mavros-msgs
sudo apt install ros-humble-cv-bridge ros-humble-image-transport

# Python 依赖
pip install mediapipe opencv-python numpy psutil
```

### 编译

```bash
cd ros2_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

### 运行测试

```bash
# 路径规划算法测试
python3 src/drone_nav/test/test_path_planner.py

# 相机模型测试
python3 src/drone_vision/test/test_camera_model.py
```

### 启动系统

```bash
# 手势识别 (测试模式, 用摄像头)
ros2 launch drone_gesture gesture_full.launch.py test_mode:=true

# 自主导航 (测试模式)
ros2 launch drone_nav nav_test.launch.py

# 视觉跟踪 (测试模式, 用摄像头)
ros2 launch drone_vision vision_test.launch.py
```

## 硬件配置

| 设备 | 型号 | 用途 |
|------|------|------|
| 机载计算机 | Jetson Nano (JetPack 5.x) | 运行 ROS2 + 算法 |
| 飞控 | 雷迅 V5+ (ArduCopter) | 飞行控制 |
| 摄像头 | 思翼 A8Mini | RTSP 视频流 |
| 连接 | UART /dev/ttyTHS1 | Jetson ↔ V5+ TELEM |

## 学习路线建议

1. **先跑通测试模式** — 不需要硬件，用摄像头就能测试手势识别和视觉跟踪
2. **读 path_planner.py** — A* 和 RRT 的实现有详细注释，适合学习路径规划
3. **读 camera_model.py** — 理解相机投影模型，这是视觉SLAM/跟踪的基础
4. **读 gesture_commander.py** — 状态机设计模式，飞控命令发送方式
5. **在 SITL 中仿真** — 用 PX4 SITL + MAVROS 测试完整流程

## 技术栈

- **ROS2 Humble** — 节点通信框架
- **MAVROS** — ROS2 ↔ MAVLink 桥接
- **MediaPipe Hands** — 手部关键点检测
- **OpenCV** — 图像处理、目标检测
- **ArduCopter/PX4** — 飞控固件

## License

MIT
