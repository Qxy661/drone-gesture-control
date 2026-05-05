# 速查手册

## ROS2 常用命令

```bash
# 构建
cd ~/ros2_ws && colcon build --packages-select <pkg>
source install/setup.bash

# 运行节点
ros2 run <pkg> <node>
ros2 launch <pkg> <launch_file>

# 话题
ros2 topic list
ros2 topic echo /<topic>
ros2 topic hz /<topic>
ros2 topic pub /<topic> <msg_type> "<data>"

# 服务
ros2 service list
ros2 service call /<service> <srv_type> "<args>"

# 参数
ros2 param list /<node>
ros2 param get /<node> <param>
ros2 param set /<node> <param> <value>
```

## MAVROS 常用 Topic/Service

```bash
# 状态
/mavros/state              # 飞控连接状态
/mavros/battery            # 电池状态
/mavros/global_position/global  # GPS 位置
/mavros/local_position/pose     # 局部位置

# 控制
/mavros/setpoint_position/local  # 位置设定点
/mavros/setpoint_velocity/cmd_vel # 速度设定点

# 服务
/mavros/cmd/arming         # 解锁/锁定
/mavros/set_mode           # 切换模式
```

## 手势方案

| 手势 | GestureID | 离散模式 | 连续模式 |
|------|-----------|---------|---------|
| 张开手掌 | OPEN_PALM=1 | 起飞 | 启用速度控制 |
| 握拳 | FIST=2 | 降落 | 停止控制 |
| 竖拇指 | THUMBS_UP=3 | 前进 | - |
| OK手势 | OK_SIGN=4 | 功能键 | - |

## 坐标系速查

| 坐标系 | 轴方向 | 用于 |
|--------|--------|------|
| ENU | x=东, y=北, z=上 | ROS 标准 |
| NED | x=北, y=东, z=下 | 飞控标准 |
| Body | x=前, y=右, z=下 | 机体系 |

## PID 调参口诀

```
先P后D再I:
P 从小到大 → 响应变快 → 出现振荡就停
D 从小到大 → 抑制振荡 → 噪声变大就停
I 从小到大 → 消除稳态误差 → 超调变大就停
```

## 卡尔曼滤波五步

```
1. 预测状态: x̂⁻ = F * x̂
2. 预测协方差: P⁻ = F * P * Fᵀ + Q
3. 计算增益: K = P⁻ * Hᵀ * (H * P⁻ * Hᵀ + R)⁻¹
4. 更新状态: x̂ = x̂⁻ + K * (z - H * x̂⁻)
5. 更新协方差: P = (I - K * H) * P⁻
```
