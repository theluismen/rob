
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math


class WallFollower(Node):

    def __init__(self):
        super().__init__('wall_follower')

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            10
        )

        self.cmd = Twist()
        self.scan = None

        # Parámetros
        self.desired_distance = 0.5   # distancia a la pared
        self.front_threshold = 0.6    # obstáculo frontal
        self.kp = 1.0                 # ganancia proporcional

        # loop de control
        self.timer = self.create_timer(0.1, self.control_loop)

    # =========================
    def laser_callback(self, msg):
        self.scan = msg

    # =========================
    def get_range(self, index):
        if self.scan is None:
            return float('inf')

        val = self.scan.ranges[index]
        if math.isinf(val):
            return 10.0
        return val

    # =========================
    def control_loop(self):
        if self.scan is None:
            return

        n = len(self.scan.ranges)

        front = self.get_range(n // 2)
        right = self.get_range(n // 4)

        # DEBUG
        self.get_logger().info(
            f"front: {front:.2f} right: {right:.2f}"
        )

        # 🚧 obstáculo delante
        if front < self.front_threshold:
            self.cmd.linear.x = 0.0
            self.cmd.angular.z = 0.8   # girar izquierda fuerte

        else:
            # 🎯 control proporcional para seguir pared derecha
            error = self.desired_distance - right

            self.cmd.linear.x = 0.2
            self.cmd.angular.z = self.kp * error

        self.pub.publish(self.cmd)


def main():
    rclpy.init()
    node = WallFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
