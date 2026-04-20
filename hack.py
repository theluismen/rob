import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math


class MazeSolver(Node):

    def __init__(self):
        super().__init__('maze_solver')

        # Publisher y Subscriber
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            10
        )

        self.cmd = Twist()
        self.laser_msg = None

        # Parámetros
        self.turn_speed = 0.5
        self.front_threshold = 1.0

        # Timer principal (control loop)
        self.timer = self.create_timer(0.1, self.control_loop)  # 10 Hz

    # =========================
    # CALLBACK
    # =========================
    def laser_callback(self, msg):
        self.laser_msg = msg

    # =========================
    # UTILIDADES
    # =========================
    def get_laser(self, pos):
        if self.laser_msg is None:
            return float('inf')

        val = self.laser_msg.ranges[pos]

        if math.isinf(val):
            return 10.0
        return val

    # =========================
    # MOVIMIENTO
    # =========================
    def stop(self):
        self.cmd.linear.x = 0.0
        self.cmd.angular.z = 0.0

    def forward(self):
        self.cmd.linear.x = 0.2
        self.cmd.angular.z = 0.0

    def turn_right(self):
        self.cmd.linear.x = 0.0
        self.cmd.angular.z = -self.turn_speed

    def turn_left(self):
        self.cmd.linear.x = 0.0
        self.cmd.angular.z = self.turn_speed

    # =========================
    # CONTROL PRINCIPAL
    # =========================
    def control_loop(self):
        if self.laser_msg is None:
            return

        front = self.get_laser(0)
        right = self.get_laser(90)
        left = self.get_laser(270)

        self.get_logger().info(
            f"Front: {front:.2f} Right: {right:.2f} Left: {left:.2f}"
        )

        if front > self.front_threshold:
            # avanzar
            self.forward()
        else:
            # elegir mejor dirección
            if right > left:
                self.turn_right()
            else:
                self.turn_left()

        self.pub.publish(self.cmd)


def main():
    rclpy.init()
    node = MazeSolver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
