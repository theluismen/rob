import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import termios
import tty
import select

def get_key(settings):
    # Ponemos la terminal en modo raw
    tty.setraw(sys.stdin.fileno())
    # select mira si hay algo que leer en stdin (espera 0.1 segundos)
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    # Restauramos la configuración original de la terminal
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, settings)
    return key

def main():
    # Guardamos la configuración original de la terminal una sola vez
    settings = termios.tcgetattr(sys.stdin.fileno())

    rclpy.init()
    node = Node("publica_vel")
    pub = node.create_publisher(Twist, 'cmd_vel', 10)

    twist = Twist()
    print("Controles: W (adelante), X (atrás), A (izq), D (der), S (parar).")
    print("Presiona Ctrl+C para salir.")

    try:
        while rclpy.ok():
            # Intentamos obtener la tecla sin bloquear el bucle
            key = get_key(settings)

            if key == 'w':
                twist.linear.x  = 0.2
                twist.angular.z = 0.0
            elif key == 'x':
                twist.linear.x  = -0.2
                twist.angular.z = 0.0
            elif key == 'a':
                twist.angular.z = 0.5
            elif key == 'd':
                twist.angular.z = -0.5
            elif key == 's':
                twist.linear.x = 0.0; twist.angular.z = 0.0
            elif key == '\x03':  # Detecta Ctrl+C manual por si acaso
                break

            pub.publish(twist)
            rclpy.spin_once(node, timeout_sec=0.1)

    except KeyboardInterrupt:
        print("\nInterrupción detectada...")
    finally:
        # Al salir, enviamos velocidad cero y limpiamos
        stop_twist = Twist()
        pub.publish(stop_twist)
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
