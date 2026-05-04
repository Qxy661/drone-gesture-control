#!/usr/bin/env python3
"""
MAVROS SITL Launch 文件
连接 MAVROS 到 PX4 SITL 仿真器

用法: ros2 launch drone_utils mavros_sitl.launch.py
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        # MAVROS 节点 - 连接到 PX4 SITL
        Node(
            package='mavros',
            executable='mavros_node',
            name='mavros',
            output='screen',
            parameters=[{
                # PX4 SITL 通过 UDP 14540 发送 MAVLink
                'fcu_url': 'udp://127.0.0.1:14540@14550',
                'gcs_url': '',
                'tgt_system': 1,
                'tgt_component': 1,
                'fcu_protocol': 'v2.0',
                'namespace': 'mavros',
                # 常用插件列表
                'pluginlists_yaml': '',
                'config_yaml': '',
            }],
            remappings=[
                # 可以在这里重映射话题
            ],
        ),
    ])
