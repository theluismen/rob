import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import math

class NavegadorLaberinto(Node):
    def __init__(self):
        super().__init__('navegador_laberinto')
        
        # Publicador para mover el robot
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        
        # Suscriptor al LIDAR (sensor de distancias)
        self.subscription_scan = self.create_subscription(
            LaserScan,
            'scan',
            self.lidar_callback,
            10)
        
        # Suscriptor a la Odometría (para detectar la meta en simulación)
        self.subscription_odom = self.create_subscription(
            Odometry,
            'odom',
            self.odom_callback,
            10)

        self.twist = Twist()
        self.meta_alcanzada = False
        
        # Coordenadas de la salida (debes ajustarlas según tu meta_sim.py)
        # Por defecto ponemos un ejemplo, cámbialas tras llegar manualmente a la meta
        self.meta_x = 2.0 
        self.meta_y = 2.0
        self.umbral_meta = 0.3 # Distancia para considerar que ha llegado

    def odom_callback(self, msg):
        # Cálculo de distancia a la meta (Simulación) [cite: 262, 263]
        pos = msg.pose.pose.position
        dist_meta = math.sqrt((pos.x - self.meta_x)**2 + (pos.y - self.meta_y)**2)
        
        if dist_meta < self.umbral_meta:
            self.meta_alcanzada = True
            self.get_logger().info("¡META ALCANZADA!")

    def lidar_callback(self, msg):
        if self.meta_alcanzada:
            self.stop_robot()
            return

        # El PDF dice: 0 (delante), 90 (izq), 180 (detrás), 270 (derecha) 
        # La tabla 'ranges' tiene 360 posiciones [cite: 251]
        dist_frontal = msg.ranges[0]
        dist_izquierda = msg.ranges[90]
        dist_derecha = msg.ranges[270]

        # Lógica simple de evitación y seguimiento:
        # 1. Si hay obstáculo delante, girar.
        # 2. Si está muy cerca de una pared lateral, corregir.
        # 3. Si hay camino libre, avanzar.

        linear_x = 0.1  # Velocidad de avance constante
        angular_z = 0.0

        if dist_frontal < 0.5: # Obstáculo cerca delante [cite: 186]
            linear_x = 0.0
            angular_z = 0.5   # Girar para buscar salida
        elif dist_izquierda < 0.3: # Demasiado cerca de pared izquierda
            linear_x = 0.0
            angular_z = -0.3  # Corregir hacia la derecha
        elif dist_derecha < 0.3:   # Demasiado cerca de pared derecha
            linear_x = 0.0
            angular_z = 0.3   # Corregir hacia la izquierda

        self.send_velocity(linear_x, angular_z)

    def send_velocity(self, linear, angular):
        self.twist.linear.x = linear
        self.twist.angular.z = angular
        self.publisher_.publish(self.twist)

    def stop_robot(self):
        self.send_velocity(0.0, 0.0)

def main(args=None):
    rclpy.init(args=args)
    nodo = NavegadorLaberinto()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        nodo.stop_robot()
    finally:
        nodo.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
