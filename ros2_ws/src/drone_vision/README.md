# drone_vision

视觉目标跟踪 — YOLOv8 检测 + 卡尔曼滤波跟踪 + 视觉伺服

## Modules

| Module | File | 可独立使用 | 功能 |
|--------|------|-----------|------|
| camera_model | camera_model.py | Yes | 针孔相机模型 |
| kalman_tracker | kalman_tracker.py | Yes | 卡尔曼滤波 + 多目标跟踪 |
| target_detector | target_detector.py | No (ROS) | OpenCV 目标检测 |
| yolo_detector | yolo_detector.py | No (ROS) | YOLOv8 通用检测 |
| visual_servo | visual_servo.py | No (ROS) | PID 视觉伺服 |
| tracking_manager | tracking_manager.py | No (ROS) | 跟踪任务编排 |

## Launch

```bash
# 测试模式 (用摄像头)
ros2 launch drone_vision vision_test.launch.py

# 真机模式 (RTSP + MAVROS)
ros2 launch drone_vision vision_system.launch.py
```

## 测试

```bash
python3 src/drone_vision/test/test_camera_model.py
python3 src/drone_vision/test/test_kalman.py
```
