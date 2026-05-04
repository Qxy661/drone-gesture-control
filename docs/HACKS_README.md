# 环境中的临时修改说明

## /usr/local/bin/rosversion
- 原因: PX4 gazebo-classic 的 FindMAVLink.cmake 需要  获取 ROS_DISTRO
- ROS2 没有这个命令，所以手动创建
- 仅在重新编译 gazebo-classic 插件时需要
- 删除条件: 不再需要编译 gazebo-classic 插件时

## /usr/include/mavlink/
- 原因: ROS2 的 ros-humble-mavlink 包版本与 PX4 不兼容
- 从 PX4 自带的 mavlink 子模块用 pymavlink 生成的头文件
- 仅在编译时需要（运行时 .so 已经链接好了）
- 删除条件: 不再需要编译 gazebo-classic 插件时

## /root/PX4-Autopilot/Tools/simulation/gazebo-classic/sitl_gazebo-classic/build/
- 39个 .so 插件文件
- 这些是 PX4 + Gazebo 仿真的核心
- 不要删除
