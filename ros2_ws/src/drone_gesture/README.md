# drone_gesture

手势识别控制系统 — MediaPipe Hands + MAVROS

## Nodes

| Node | File | 功能 |
|------|------|------|
| gesture_recognizer | gesture_recognizer.py | 视频流手势识别 |
| gesture_commander | gesture_commander.py | 手势→飞控命令 (离散) |
| gesture_velocity_controller | gesture_velocity_controller.py | 手势→连续速度控制 |
| safety_monitor | safety_monitor.py | 电量/连接/心跳监控 |
| diagnostics | diagnostics.py | 系统诊断聚合 |

## Launch

```bash
# 测试模式 (用摄像头, 不连飞控)
ros2 launch drone_gesture gesture_full.launch.py test_mode:=true

# 真机模式
ros2 launch drone_gesture gesture_full.launch.py test_mode:=false
```

## 手势方案

| 手势 | 离散模式 | 连续模式 |
|------|---------|---------|
| 张开手掌 | 起飞 | 启用速度控制 |
| 握拳 | 降落 | 停止控制 |
| 竖拇指 | 前进 | - |
| OK手势 | 功能键 | - |
