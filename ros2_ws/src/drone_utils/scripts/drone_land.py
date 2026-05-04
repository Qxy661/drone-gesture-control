"""
无人机降落脚本 (ROS2 + MAVROS)

用法: ros2 run drone_utils drone_land
"""

import rclpy
from rclpy.node import Node
from mavros_msgs.msg import State
from mavros_msgs.srv import SetMode


class LandNode(Node):
    def __init__(self):
        super().__init__('drone_land')
        self.state = None
        self.create_subscription(State, '/mavros/state', self._state_cb, 10)
        self.mode_cli = self.create_client(SetMode, '/mavros/set_mode')
        self.timer = self.create_timer(1.0, self._tick)
        self.sent = False

    def _state_cb(self, msg):
        self.state = msg

    def _tick(self):
        if self.state is None or self.sent:
            return
        self.get_logger().info('发送降落指令...')
        req = SetMode.Request()
        req.custom_mode = 'LAND'
        self.mode_cli.call_async(req)
        self.sent = True
        self.get_logger().info('降落指令已发送')


def main():
    rclpy.init()
    node = LandNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
