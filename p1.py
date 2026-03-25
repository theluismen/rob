import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import termios
import tty
import select  # <-- afegit

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    if len(sys.argv) != 3:
        print('Fer: ', sys.argv[0], " lin ang")
        exit(-1)

    lin = float(sys.argv[1])
    ang = float(sys.argv[2])

    rclpy.init()
    node = Node("publica_vel")
    pub = node.create_publisher(Twist, 'cmd_vel', 10)

    twist = Twist()
    twist.linear.x = lin
    twist.angular.z = ang

    print("Prem dos returns tecla per aturar i sortir...")
    try:
        while rclpy.ok():
            pub.publish(twist)
            rclpy.spin_once(node, timeout_sec=0.1)
            # aquí fem servir select per veure si hi ha tecla
#            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            key = get_key()
            if key == 'w':
                print("Avanza")
            elif key == 'x':
                print("Patras")
            elif key == 'a':
                print("Izquierda")
            elif key == 'd':
                print("Derecha")
            elif key == 's':
                print("Parar")
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        stop_twist = Twist()  # velocitat zero
        pub.publish(stop_twist)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
