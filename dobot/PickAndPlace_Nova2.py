import threading

from time import sleep
from Garra_URV_api import Gripper
from Utils_URV_Nova_api import Robot


if __name__ == '__main__':

    dsb, mv, feed,feedFour, ip = Robot.ConnectRobot()

    feed_thread = threading.Thread(target=Robot.GetFeed, args=(feedFour,))
    feed_thread.daemon = True
    feed_thread.start()

    feed_thread1 = threading.Thread(target=Robot.ClearRobotError, args=(dsb,))
    feed_thread1.daemon = True
    feed_thread1.start()


    print("[+] - Habilitando el robot...")
    dsb.EnableRobot()

    print("[+] - Habilitando la pinza...")
    gr = Gripper(dsb, mv, ip)



    P1 = [0,-364, 105.000000, 180.000000, 0.000000, 0.000000]
    P2 = [0,-364, 205.000000, 180.000000, 0.000000, 0.000000]
    P3 = [100, -364, 105.000000, 180.000000, 0.000000, 0.000000]
    P4 = [100, -364, 205.000000, 180.000000, 0.000000, 0.000000]

    mv.JointMovJ(0,0,0,0,0,0,60,50)
    mv.MovJ(P2[0], P2[1], P2[2], P2[3], P2[4], P2[5])
    mv.Sync()
    dsb.SpeedFactor(10)
    mv.MovJ(P1[0], P1[1], P1[2], P1[3], P1[4], P1[5])
    gr.Close()
    mv.RelMovLUser(0,0,50,0,0,0,0,10)
    dsb.SpeedFactor(80)
    mv.MovJ(P4[0], P4[1], P4[2], P4[3], P4[4], P4[5])
    mv.Sync()
    dsb.SpeedFactor(10)
    mv.MovJ(P3[0], P3[1], P3[2], P3[3], P3[4], P3[5])
    gr.Open()
    mv.RelMovLUser(0,0,50,0,0,0,0,10)
    dsb.SpeedFactor(80)
    mv.MovJ(P4[0], P4[1], P4[2], P4[3], P4[4], P4[5])
    mv.JointMovJ(0,0,0,0,0,0,60,50)
