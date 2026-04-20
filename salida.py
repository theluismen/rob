import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class State():
	@abstractmethod
	def do(self):
		pass
	
class Palante(State):
	
	def do()
	
class SeguidorParet(Node):
    def __init__(self):
        super().__init__('seguidor_paret')
        
        # Publicador para enviar comandos de velocidad al tópico cmd_vel 
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        
        # Suscriptor para recibir datos del LIDAR desde el tópico /scan [cite: 127, 130]
        self.subscription = self.create_subscription(
            LaserScan, 
            'scan', 
            self.listener_callback, 
            10)
        
        # Parámetros de control
        self.distancia_desitjada = 0.2  # Distancia que queremos mantener con la pared (metros)
        self.velocitat_lineal = 0.1     # Velocidad de avance 
        
        self.get_logger().info('Algorisme de seguiment de paret dreta iniciat')

    def listener_callback(self, msg):
        
        davant = msg.ranges[0]
        dreta = msg.ranges[270]
        
        move = Twist()

        # 1. EMERGENCIA: Si hay una pared justo delante, girar a la izquierda
        if davant < 0.25:
            move.linear.x = 0.0
            move.angular.z = 1.3  # Giro positivo = izquierda [cite: 59, 82]
        
        # 2. SEGUIMIENTO: Si no hay obstáculo inmediato delante, ajustar según la pared derecha
        else:
            move.linear.x = self.velocitat_lineal
            
            if dreta > self.distancia_desitjada + 0.1:
                # Demasiado lejos de la pared: girar un poco a la derecha (negativo)
                move.angular.z = -0.4
            elif dreta < self.distancia_desitjada - 0.1:
                # Demasiado cerca: alejarse de la pared girando a la izquierda (positivo)
                move.angular.z = 0.4
            else:
                # Distancia correcta: seguir recto
                move.angular.z = 0.0

        self.publisher.publish(move)

    def stop_robot(self):
        # Envía un mensaje vacío para detener el movimiento [cite: 61, 85]
        self.publisher.publish(Twist())

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
