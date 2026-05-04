"""
无人机起飞脚本 (ROS2 + MAVROS)
连接 PX4 SITL 或 ArduCopter, 解锁并起飞到指定高度

用法: ros2 run drone_utils drone_takeoff
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, SetMode


class TakeoffNode(Node):
    def __init__(self):
        super().__init__('drone_takeoff')
        self.declare_parameter('altitude', 2.0)
        self.alt = self.get_parameter('altitude').value

        self.state = None
        self.state_sub = self.create_subscription(State, '/mavros/state', self._state_cb, 10)
        self.pos_pub = self.create_publisher(PoseStamped, '/mavros/setpoint_position/local', 10)
        self.arm_cli = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_cli = self.create_client(SetMode, '/mavros/set_mode')

        self.get_logger().info(f'等待 MAVROS 连接...')
        self.timer = self.create_timer(0.5, self._tick)
        self.step = 0

    def _state_cb(self, msg):
        self.state = msg

    def _tick(self):
        if self.state is None:
            return

        if self.step == 0:
            # 切换 GUIDED 模式
            self.get_logger().info(f'设置 GUIDED 模式...')
            req = SetMode.Request()
            req.custom_mode = 'GUIDED'
            self.mode_cli.call_async(req)
            self.step = 1

        elif self.step == 1:
            if self.state.mode == 'GUIDED' or self.state.mode == 'GUIDED':
                self.get_logger().info('已进入 GUIDED 模式, 解锁...')
                req = CommandBool.Request()
                req.value = True
                self.arm_cli.call_async(req)
                self.step = 2

        elif self.step == 2:
            if self.state.armed:
                self.get_logger().info(f'已解锁, 起飞到 {self.alt}m...')
                msg = PoseStamped()
                msg.header.stamp = self.get_clock().now().to_msg()
                msg.pose.position.z = self.alt
                self.pos_pub.publish(msg)
                self.step = 3

        elif self.step == 3:
            self.get_logger().info(f'起飞指令已发送, 目标高度: {self.alt}m', throttle_duration_sec=2.0)


def main():
    rclpy.init()
    node = TakeoffNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
