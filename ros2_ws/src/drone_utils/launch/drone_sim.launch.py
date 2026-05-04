#!/usr/bin/env python3
"""
完整无人机仿真 Launch 文件
启动 PX4 SITL + Gazebo Classic + MAVROS

用法: ros2 launch drone_utils drone_sim.launch.py

注意: Gazebo GUI 需要先手动启动 gzserver 和 gzclient
      或者使用 start_drone_sim.sh 脚本
"""

import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    # PX4 路径配置
    px4_root = '/root/PX4-Autopilot'
    build_path = os.path.join(px4_root, 'build/px4_sitl_default')
    gz_build = os.path.join(px4_root, 'Tools/simulation/gazebo-classic/sitl_gazebo-classic/build')
    model_path = os.path.join(px4_root, 'Tools/simulation/gazebo-classic/sitl_gazebo-classic/models')
    
    # 环境变量
    env = {
        'DISPLAY': ':0',
        'GAZEBO_PLUGIN_PATH': gz_build,
        'GAZEBO_MODEL_PATH': model_path,
        'LD_LIBRARY_PATH': gz_build + ':' + os.environ.get('LD_LIBRARY_PATH', ''),
        'PX4_SIM_MODEL': 'gazebo-classic_iris',
        'PX4_SIM_WORLD': 'empty',
        'PATH': os.path.join(build_path, 'bin') + ':' + os.path.join(build_path, 'rootfs') + ':' + os.environ.get('PATH', ''),
    }
    
    return LaunchDescription([
        # 1. 启动 Gazebo 服务器
        ExecuteProcess(
            cmd=['gzserver', '--verbose', 
                 os.path.join(px4_root, 'Tools/simulation/gazebo-classic/sitl_gazebo-classic/worlds/empty.world')],
            output='screen',
            additional_env=env,
        ),
        
        # 2. 延迟启动 Gazebo 客户端
        TimerAction(
            period=3.0,
            actions=[
                ExecuteProcess(
                    cmd=['gzclient'],
                    output='screen',
                    additional_env=env,
                ),
            ],
        ),
        
        # 3. 延迟生成无人机模型
        TimerAction(
            period=5.0,
            actions=[
                ExecuteProcess(
                    cmd=['gz', 'model', '--spawn-file',
                         os.path.join(model_path, 'iris/iris.sdf'),
                         '--model-name', 'iris', '-x', '0', '-y', '0', '-z', '0.3'],
                    output='screen',
                    additional_env=env,
                ),
            ],
        ),
        
        # 4. 延迟启动 PX4
        TimerAction(
            period=8.0,
            actions=[
                ExecuteProcess(
                    cmd=['px4', '-s', 'etc/init.d-posix/rcS'],
                    cwd=os.path.join(build_path, 'rootfs'),
                    output='screen',
                    additional_env=env,
                ),
            ],
        ),
        
        # 5. 延迟启动 MAVROS
        TimerAction(
            period=12.0,
            actions=[
                Node(
                    package='mavros',
                    executable='mavros_node',
                    name='mavros',
                    output='screen',
                    parameters=[{
                        'fcu_url': 'udp://127.0.0.1:14540@14550',
                        'gcs_url': '',
                        'tgt_system': 1,
                        'tgt_component': 1,
                        'fcu_protocol': 'v2.0',
                        'namespace': 'mavros',
                    }],
                ),
            ],
        ),
    ])
