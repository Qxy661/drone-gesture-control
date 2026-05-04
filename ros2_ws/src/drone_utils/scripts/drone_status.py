"""
无人机状态监控脚本 (ROS2 + MAVROS)
实时显示飞控连接状态、飞行模式、解锁状态

用法: ros2 run drone_utils drone_status
"""

import rclpy
from rclpy.node import Node
from mavros_msgs.msg import State


class StatusNode(Node):
    def __init__(self):
        super().__init__('drone_status')
        self.create_subscription(State, '/mavros/state', self._state_cb, 10)

    def _state_cb(self, msg):
        armed = 'YES' if msg.armed else 'NO'
        conn = 'YES' if msg.connected else 'NO'
        self.get_logger().info(
            f'连接: {conn} | 模式: {msg.mode} | 解锁: {armed}',
            throttle_duration_sec=1.0)


def main():
    rclpy.init()
    node = StatusNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
