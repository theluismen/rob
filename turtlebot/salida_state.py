import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from abc import ABC, abstractmethod
import math


# =========================
# STATE INTERFACE
# =========================
class State(ABC):
    @abstractmethod
    def execute(self, context, msg):
        pass


# =========================
# ESTADO: AVANZAR
# =========================
class AvanzarState(State):
    def execute(self, context, msg):
        davant = msg.ranges[0]
        dreta  = msg.ranges[270]

        move = Twist()

        # Si hay obstáculo delante → cambiar a girar
        if davant < 0.2:
            context.set_state(GirarState())
            return

        # Movimiento normal
        move.linear.x = context.velocitat_lineal

        if dreta > context.distancia_desitjada + 0.05:
            move.angular.z = -0.4
        elif dreta < context.distancia_desitjada - 0.05:
            move.angular.z = 0.4
        else:
            move.angular.z = 0.0

        context.publisher.publish(move)


# =========================
# ESTADO: GIRAR IZQUIERDA
# =========================
class GirarState(State):
    def __init__(self):
        self.yaw_inicial = None

    def execute(self, context, msg):
        move = Twist()

        # Guardar yaw inicial solo una vez
        if self.yaw_inicial is None:
            self.yaw_inicial = context.yaw_actual

        move.linear.x = 0.0
        move.angular.z = 0.7

        # Calcular diferencia angular
        diff = context.yaw_actual - self.yaw_inicial

        # Normalizar entre -pi y pi
        diff = math.atan2(math.sin(diff), math.cos(diff))

        # 90 grados ≈ 1.57 radianes
        if abs(diff) >= 1.25:
            context.set_state(AvanzarState())

        context.publisher.publish(move)


# =========================
# CONTEXTO (NODE)
# =========================
class SeguidorParet(Node):
    def __init__(self):
        super().__init__('seguidor_paret')

        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)

        self.subscription = self.create_subscription(
            LaserScan,
            'scan',
            self.listener_callback,
            10
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            'odom',
            self.odom_callback,
            10
        )

        self.yaw_actual = 0.0

        self.distancia_desitjada = 0.13
        self.velocitat_lineal = 0.1

        # Estado inicial
        self.state = AvanzarState()

        self.get_logger().info('State Pattern activat')

    def set_state(self, new_state):
        self.state = new_state

    def listener_callback(self, msg):
        self.state.execute(self, msg)

    def odom_callback(self, msg):
        q = msg.pose.pose.orientation

        # Conversión a yaw (rotación en Z)
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)

        self.yaw_actual = math.atan2(siny_cosp, cosy_cosp)

    def stop_robot(self):
        self.publisher.publish(Twist())


# =========================
# MAIN
# =========================
def main(args=None):
    rclpy.init(args=args)
    seguidor = SeguidorParet()

    try:
        rclpy.spin(seguidor)
    except KeyboardInterrupt:
        seguidor.get_logger().info('Aturant el robot...')
        seguidor.stop_robot()
    finally:
        seguidor.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
