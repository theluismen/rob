
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

class SeguidorSegurTF(Node):
    def __init__(self):
        super().__init__('seguidor_segur_tf')
        
        # Publicador y Suscriptor
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.subscription = self.create_subscription(LaserScan, 'scan', self.scan_callback, 10)
        
        # Herramientas de TF2
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Parámetros físicos (TurtleBot Burger)
        self.distancia_seguretat = 0.25  # Margen para no chocar ruedas [cite: 164, 173]
        self.offset_y_roda = 0.08        # Distancia del centro a la rueda derecha
        self.lidar_offset_x = 0.0        # Se actualizará dinámicamente con TF

    def obtener_offsets(self):
        """Consulta la posición del LIDAR respecto al centro del robot"""
        try:
            # Buscamos la posición del sensor (base_scan) respecto al centro (base_link)
            t = self.tf_buffer.lookup_transform('base_link', 'base_scan', rclpy.time.Time())
            self.lidar_offset_x = t.transform.translation.x
        except TransformException:
            # Si falla, usamos valores por defecto
            pass

    def scan_callback(self, msg):
        self.obtener_offsets()
        
        # Lecturas del LIDAR (resolución 1 grado) [cite: 185, 251]
        # 0° adelante, 270° derecha pura, 315° diagonal adelante-derecha
        dist_davant = msg.ranges[0]
        dist_dreta = msg.ranges[270]
        dist_diagonal = msg.ranges[315]

        # CÁLCULO DE SEGURIDAD PARA LA RUEDA
        # Ajustamos la distancia leída sumando/restando los offsets del robot
        espai_lliure_roda = dist_dreta - self.offset_y_roda

        move = Twist()

        # LÓGICA DE CONTROL
        if dist_davant < 0.4:
            # Obstáculo frontal: Giro de seguridad a la izquierda [cite: 59, 60]
            move.linear.x = 0.02
            move.angular.z = 0.5
        elif espai_lliure_roda < 0.15 or dist_diagonal < 0.3:
            # ¡Rueda derecha en peligro! Alejarse de la pared inmediatamente
            move.linear.x = 0.05
            move.angular.z = 0.3
        elif dist_dreta > self.distancia_seguretat + 0.1:
            # Demasiado lejos de la pared: Acercarse suavemente
            move.linear.x = 0.1
            move.angular.z = -0.2
        else:
            # Distancia óptima: Avanzar recto [cite: 82, 84]
            move.linear.x = 0.15
            move.angular.z = 0.0

        self.publisher.publish(move)

    def stop_robot(self):
        self.publisher.publish(Twist())

def main():
    rclpy.init()
    node = SeguidorSegurTF()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.stop_robot()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
