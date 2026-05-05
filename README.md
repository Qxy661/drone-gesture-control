# Drone Autonomy Suite

基于 ROS2 Humble 的无人机自主飞行系统。四个子项目覆盖 **感知→决策→控制→降落** 全链路。

## 架构

```
┌─────────────────────── ROS2 Humble ───────────────────────┐
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ drone_gesture│  │  drone_nav   │  │ drone_vision │    │
│  │ 手势识别+控制 │  │ 导航+路径规划 │  │ 视觉目标跟踪 │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                  │             │
│         └─────────┬───────┴──────────────────┘             │
│                   │                                        │
│            ┌──────▼───────┐  ┌──────────────┐             │
│            │    MAVROS     │  │ drone_landing │             │
│            └──────┬───────┘  │ 精准视觉降落  │             │
│                   │          └──────┬───────┘             │
└───────────────────┼─────────────────┼─────────────────────┘
                    │ UART            │
             ┌──────▼─────────────────▼──────┐
             │       飞控 V5+ (ArduCopter)    │
             └────────────────────────────────┘
```

## 项目列表

| 包 | 功能 | 核心技术 | 代码量 |
|---|------|---------|-------|
| drone_gesture | 手势识别控制 | MediaPipe + 状态机 + 速度映射 | ~1200行 |
| drone_nav | 自主导航 | A*/RRT/RRT* + DWA + 坐标转换 | ~1000行 |
| drone_vision | 视觉跟踪 | YOLOv8 + 卡尔曼滤波 + 视觉伺服 | ~1300行 |
| drone_landing | 精准降落 | ArUco + PnP 6DOF + 级联PID | ~800行 |

## 技术亮点

| 特性 | 实现 | 文件 |
|------|------|------|
| 连续手势速度控制 | 低通滤波+死区+sigmoid映射 | gesture_velocity_controller.py |
| A*/RRT/RRT* 路径规划 | 栅格搜索+随机采样+渐近最优 | path_planner.py |
| DWA 局部避障 | 速度空间采样+轨迹评价+动力学约束 | dwa_planner.py |
| 卡尔曼滤波跟踪 | 状态估计+遮挡预测+多目标管理 | kalman_tracker.py |
| YOLOv8 目标检测 | 通用检测+实时跟踪 | yolo_detector.py |
| PID 视觉伺服 | CENTER/FOLLOW/CIRCLE 三模式 | visual_servo.py |
| ArUco 6DOF 位姿 | solvePnP+迭代优化 | aruco_pose.py |
| 精准降落控制 | 级联PID+5阶段状态机 | landing_controller.py |
| 安全监控 | 电量/连接/心跳+自动紧急降落 | safety_monitor.py |
| 系统诊断 | CPU/内存/FPS 聚合+服务查询 | diagnostics.py |

## 快速开始

```bash
# 编译
cd ros2_ws && source /opt/ros/humble/setup.bash
colcon build && source install/setup.bash

# 运行测试
python3 src/drone_nav/test/test_path_planner.py
python3 src/drone_nav/test/test_dwa.py
python3 src/drone_vision/test/test_camera_model.py
python3 src/drone_vision/test/test_kalman.py
python3 src/drone_landing/test/test_aruco_pose.py

# 启动系统 (测试模式, 不需要硬件)
ros2 launch drone_gesture gesture_full.launch.py test_mode:=true
ros2 launch drone_nav nav_test.launch.py
ros2 launch drone_vision vision_test.launch.py
ros2 launch drone_landing landing_test.launch.py
```

## 依赖

```bash
sudo apt install ros-humble-mavros ros-humble-mavros-msgs
sudo apt install ros-humble-cv-bridge ros-humble-image-transport
pip install mediapipe opencv-python numpy psutil
pip install ultralytics  # YOLOv8 (可选)
```

## 硬件

| 设备 | 型号 | 用途 |
|------|------|------|
| 机载计算机 | Jetson Nano (JetPack 5.x) | ROS2 + 算法 |
| 飞控 | 雷迅 V5+ (ArduCopter) | 飞行控制 |
| 摄像头 | 思翼 A8Mini | RTSP 视频流 |

## License

MIT
