import threading
import argparse

from time import sleep
from Garra_URV_api import Gripper
from Utils_URV_Nova_api import Robot


def hanoi(mv, dsb, gr, n, origen, destino, auxiliar, torres, alturas):
    if n == 1:
        pick_and_place(mv, dsb, gr, torres, origen, destino, alturas)
        return

    hanoi(mv, dsb, gr, n - 1, origen, auxiliar, destino, torres, alturas)

    pick_and_place(mv, dsb, gr, torres, origen, destino, alturas)

    hanoi(mv, dsb, gr, n - 1, auxiliar, destino, origen, torres, alturas)


def pick_and_place(mv, dsb, gr, torres, origen, destino, alturas, vel_fast=80, vel_slow=10):
    """
    Realiza un ciclo de Pick and Place y finaliza en el punto de seguridad de destino.
    p_pick: Coordenadas reales de agarre [X, Y, Z, R, J, W]
    p_place: Coordenadas reales de entrega [X, Y, Z, R, J, W]
    """
    techo  = 250.00
    base   = 102.00
    offset = 10.00

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

    parser = argparse.ArgumentParser(description="DoBot Hanoi")
    parser.add_argument("-n", "--n", type=int, default=3, help="Numero de Discos")
    args = parser.parse_args()

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

    torres = {
        "A": [-120,-364, 0.000000, 180.000000, 0.000000, 0.000000],
        "B": [   0,-364, 0.000000, 180.000000, 0.000000, 0.000000],
        "C": [ 120,-364, 0.000000, 180.000000, 0.000000, 0.000000]
    }

    alturas = {
        "A": [i for i in range(args.n,0,-1)], # Pila Discos Inicial
        "B": [],
        "C": []
    }

    mv.JointMovJ(0,0,0,0,0,0,60,50)

    init_point = [0,-364, 205.000000, 180.000000, 0.000000, 0.000000]

    mv.MovJ(init_point[0], init_point[1], init_point[2], init_point[3], init_point[4], init_point[5])

    hanoi(mv, dsb, gr, args.n, "A", "C", "B", torres, alturas)

    mv.JointMovJ(0,0,0,0,0,0,60,50)
