import threading
import argparse

from time import sleep
from Garra_URV_api import Gripper
from Utils_URV_Nova_api import Robot

# Variables globales
VEL_FAST=80
VEL_SLOW=10

techo  = 250.00
base   = 102.00
offset = 10.00

torres = {
	"A": [-120,-364, 0.000000, 180.000000, 0.000000, 0.000000],
	"B": [   0,-364, 0.000000, 180.000000, 0.000000, 0.000000],
	"C": [ 120,-364, 0.000000, 180.000000, 0.000000, 0.000000]
}


def hanoi(mv, dsb, gr, n, origen, destino, auxiliar, alturas, vel_fast, vel_slow):
    if n == 1:
        pick_and_place(mv, dsb, gr, origen, destino, alturas, vel_fast, vel_slow)
        return

    hanoi(mv, dsb, gr, n - 1, origen, auxiliar, destino, alturas, vel_fast, vel_slow)

    pick_and_place(mv, dsb, gr, origen, destino, alturas, vel_fast, vel_slow)

    hanoi(mv, dsb, gr, n - 1, auxiliar, destino, origen, alturas, vel_fast, vel_slow)


def pick_and_place(mv, dsb, gr, origen, destino, alturas, vel_fast, vel_slow):
    """
    Realiza un ciclo de Pick and Place y finaliza en el punto de seguridad de destino.
    p_pick: Coordenadas reales de agarre [X, Y, Z, R, J, W]
    p_place: Coordenadas reales de entrega [X, Y, Z, R, J, W]
    """

    p_pick     = torres[origen].copy()
    p_pick[2]  = base + len(alturas[origen]) * offset

    p_place    = torres[destino].copy()
    p_place[2] = base + (len(alturas[destino])+1) * offset

    disco = alturas[origen].pop()
    alturas[destino].append(disco)

    print(f"Iniciando ciclo: Yendo a recoger a {p_pick}")

    # --- FASE DE RECOGIDA (PICK) ---
    # 1. Ir al punto de seguridad de recogida
    dsb.SpeedFactor(vel_fast)
    mv.MovJ(p_pick[0], p_pick[1], techo, p_pick[3], p_pick[4], p_pick[5])
    mv.Sync()

    # 2. Bajar suavemente al punto de agarre
    dsb.SpeedFactor(vel_slow)
    mv.MovL(p_pick[0], p_pick[1], p_pick[2], p_pick[3], p_pick[4], p_pick[5])

    # 3. Cerrar la pinza
    gr.Close()

    # 4. Retiro vertical de seguridad
    mv.RelMovLUser(0, 0, 50, 0, 0, 0, 0, vel_slow)
    mv.Sync()

    # --- FASE DE ENTREGA (PLACE) ---
    # 5. Desplazarse rápido al punto de seguridad de entrega
    dsb.SpeedFactor(vel_fast)
    mv.MovJ(p_place[0], p_place[1], techo, p_place[3], p_place[4], p_place[5])
    mv.Sync()

    # 6. Bajar suavemente al punto de descarga
    dsb.SpeedFactor(vel_slow)
    mv.MovL(p_place[0], p_place[1], p_place[2], p_place[3], p_place[4], p_place[5])

    # 7. Abrir la pinza
    gr.Open()

    # 8. Retiro final al punto de seguridad (p_place)
    # Usamos MovL para asegurar una subida recta o RelMovLUser para consistencia
    mv.RelMovLUser(0, 0, 50, 0, 0, 0, 0, vel_slow)
    mv.Sync()

    print(f"Ciclo completado. Robot ubicado en punto de seguridad: {p_place}")


if __name__ == '__main__':

	# Argumentos de CLI
    parser = argparse.ArgumentParser(description="DoBot Hanoi")
    parser.add_argument("-f", "--fast", action="store_true", help="Modo Rápido")
    parser.add_argument("-n", "--n", type=int, required=True, help="Numero de Discos")
    args = parser.parse_args()

    if args.n < 3 or args.n > 5:
        exit("-n N: N tiene que estar en el intervalo [3..5]")
        
    if args.fast:
        VEL_FAST=100
        VEL_SLOW=100

	# Inicializaciones
    dsb, mv, feed,feedFour, ip = Robot.ConnectRobot()

    feed_thread = threading.Thread(target=Robot.GetFeed, args=(feedFour,))
    feed_thread.daemon = True
    feed_thread.start()

    feed_thread1 = threading.Thread(target=Robot.ClearRobotError, args=(dsb,))
    feed_thread1.daemon = True
    feed_thread1.start()

    # Habilitar Robot
    print("[+] - Habilitando el robot...")
    dsb.EnableRobot()

    # Habilitar Pinza
    print("[+] - Habilitando la pinza...")
    gr = Gripper(dsb, mv, ip)
	
	# Inicializar las alturas
    alturas = {
	    "A": [i for i in range(args.n,0,-1)], # Pila Discos Inicial
	    "B": [],
	    "C": []
    }

	# Colocarse En Posicion Normal
    mv.JointMovJ(0,0,0,0,0,0,60,50)

	# Moverse a un punto inicial
    print("[+] - Moviento Pinza a Inicio")
    dsb.SpeedFactor(VEL_FAST)
    init_point = [0,-364, 205.000000, 180.000000, 0.000000, 0.000000]
    
    mv.MovJ(init_point[0], init_point[1], init_point[2], init_point[3], init_point[4], init_point[5])
    
    init_point = torres["A"].copy()
    init_point[2] = base + len(alturas["A"]) * offset
    
    mv.MovJ(init_point[0], init_point[1], init_point[2], init_point[3], init_point[4], init_point[5])
    mv.Sync()
    
    input("[+] - Pulsa Enter para empezar...")

	# Ejecutar hanoi con pick-and-place
    hanoi(mv, dsb, gr, args.n, "A", "C", "B", alturas , VEL_FAST, VEL_SLOW)

	# Volver a Posicion Normal
    dsb.SpeedFactor(VEL_FAST)
    mv.JointMovJ(0,0,0,0,0,0,60,50)
