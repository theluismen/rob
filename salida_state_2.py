import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from abc import ABC, abstractmethod
import math
import numpy as np

# =========================
# STATE INTERFACE
# =========================
class State(ABC):
    @abstractmethod
    def execute(self, context, msg):
        pass

# =========================
# ESTADO: AVANZAR (Lógica de Distancia Máxima)
# =========================
class AvanzarState(State):
    def execute(self, context, msg):
        # 1. Filtrar datos válidos del LIDAR
        # Sustituimos valores fuera de rango (0.0 o inf) por 0 para no tomarlos como "distancia larga"
        ranges = [r if (msg.range_min < r < msg.range_max) else 0.0 for r in msg.ranges]
        
        # 2. Encontrar la distancia más larga y su ángulo
        max_dist = max(ranges)
        index_max = ranges.index(max_dist)
        
        # Calcular el ángulo en radianes basado en el índice
        # angle = angle_min + (index * angle_increment)
        angle_to_path = msg.angle_min + (index_max * msg.angle_increment)
        
        # 3. Obstáculo crítico delante (Seguridad)
        # Miramos un pequeño sector frontal (aprox. -10 a 10 grados)
        dist_frontal = msg.ranges[0] 
        if dist_frontal < 0.25:
            context.get_logger().info("¡Obstáculo detectado! Girando...")
            context.set_state(GirarState())
            return

        # 4. Movimiento hacia la zona más despejada
        move = Twist()
        move.linear.x = context.velocitat_lineal
        
        # P-Controller simple para el ángulo: 
        # Intentamos que el ángulo hacia el espacio vacío sea 0 (frente al robot)
        move.angular.z = 0.8 * angle_to_path 

        context.publisher.publish(move)

# =========================
# ESTADO: GIRAR (Mejorado para salir de bloqueos)
# =========================
class GirarState(State):
    def __init__(self):
        self.yaw_inicial = None

    def execute(self, context, msg):
        move = Twist()
        if self.yaw_inicial is None:
            self.yaw_inicial = context.yaw_actual

        move.linear.x = 0.0
        move.angular.z = 0.6  # Giro constante para buscar salida

        diff = context.yaw_actual - self.yaw_inicial
        diff = math.atan2(math.sin(diff), math.cos(diff))

        # Giramos al menos 90 grados para re-evaluar el entorno
        if abs(diff) >= 1.57:
            context.set_state(AvanzarState())

        context.publisher.publish(move)

# =========================
# CONTEXTO (NODE) - Sin cambios mayores
# =========================
class SeguidorParet(Node):
    def __init__(self):
        super().__init__('seguidor_paret')
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.subscription = self.create_subscription(LaserScan, 'scan', self.listener_callback, 10)
        self.odom_sub = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)

        self.yaw_actual = 0.0
        self.velocitat_lineal = 0.15 # Un poco más rápido para notar la fluidez
        self.state = AvanzarState()

    def set_state(self, new_state):
        self.state = new_state

    def listener_callback(self, msg):
        self.state.execute(self, msg)

    def odom_callback(self, msg):
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.yaw_actual = math.atan2(siny_cosp, cosy_cosp)

    def stop_robot(self):
        self.publisher.publish(Twist())

def main(args=None):
    rclpy.init(args=args)
    seguidor = SeguidorParet()
    try:
        rclpy.spin(seguidor)
    except KeyboardInterrupt:
        seguidor.stop_robot()
    finally:
        seguidor.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
