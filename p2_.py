import rclpy
from rclpy.node 		import Node
from geometry_msgs.msg 	import Twist
from sensor_msgs.msg 	import LaserScan
from nav_msgs.msg 		import Odometry

class Mbappe ( Node ):
	
	def __init__ ( self, id = "mbappe"):
		# Crear Nodo de ROS2
		super().__init__(id)

		# Crear Publicador de Movimiento/Velocidad (topic="/cmd_vel")
		self.pub_vel = self.create_publisher(Twist, 'cmd_vel', 10)
		
		# Crear Suscripcion a sensor LIDAR (topic="/scan")
		self.sub_lidar = self.create_subscription(
			LaserScan, '/scan', self.callback_lidar, 10)
	
		self.twist = Twist()
		
	def callback_lidar ( self, msg ):
		print(msg.ranges[0])
		
		print(min(msg.ranges))
				
		if ( msg.ranges[0] < 0.175 ):
			self.twist.linear.x  = 0.0
			self.twist.angular.z = -0.1
		elif ( msg.ranges[0] >= 0.175 and msg.ranges[0] < 0.25 ):
			for i in range(30, -30, -1):
				if ( msg.ranges[i] < 0.4 ):
					pass
			self.twist.linear.x  = 0.0
			self.twist.angular.z = -0.1
		elif (msg.ranges[0] > 0.4 ):
			self.twist.linear.x  = 0.1
			self.twist.angular.z = 0.0
			
		self.pub_vel.publish(self.twist)
		
def main():
    rclpy.init()
    rclpy.spin(Mbappe())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
