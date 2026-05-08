
from dobot_api import DobotApiDashboard, DobotApi, DobotApiMove,DobotApiFeedBack, MyType, alarmAlarmJsonFile
from dataclasses import dataclass
from typing import List
import threading
from time import sleep

import numpy as np
import re

# Variable global (coordenadas iniciales)
current_actual = [-1]
algorithm_queue = -1
enableStatus_robot = -1
robotErrorState = False
robotMode = 0
globalLockValue = threading.Lock()

class Robot:
    
    def GetFeed(feedFour: DobotApiFeedBack):
            global current_actual
            global algorithm_queue
            global enableStatus_robot
            global robotErrorState
            global robotMode
                #Obtener el estado del Robot
            while True:
                with globalLockValue:
                    feedInfo = feedFour.feedBackData()
                    if hex((feedInfo['test_value'][0])) == '0x123456789abcdef':
						# Refresh Properties
                        robotMode=feedInfo['robot_mode'][0]
                        current_actual = feedInfo["tool_vector_actual"][0]
                        algorithm_queue = feedInfo['run_queued_cmd'][0]
                        enableStatus_robot = feedInfo['enable_status'][0]
                        robotErrorState = feedInfo['error_status'][0]
                        #Agregar datos de retroalimentación personalizados
                    sleep(0.001)
					
					
    def ClearRobotError(dashboard: DobotApiDashboard):
        global robotErrorState
        dataController, dataServo = alarmAlarmJsonFile()    # Leer los códigos de alarma del controlador y del servomotor
        while True:
            globalLockValue.acquire()
            if robotErrorState:
                numbers = re.findall(r'-?\d+', dashboard.GetErrorID())
                numbers = [int(num) for num in numbers]
                if (numbers[0] == 0):
                    if (len(numbers) > 1):
                        for i in numbers[1:]:
                            alarmState = False
                            if i == -2:
                                print("Alarma de máquina, colisión de máquina", i)
                                alarmState = True
                            if alarmState:
                                continue
                            for item in dataController:
                                if i == item["id"]:
                                    print("Alarma de máquina, Controller errorid", i,
                                        item["zh_CN"]["description"])
                                    alarmState = True
                                    break
                            if alarmState:
                                continue
                            for item in dataServo:
                                if i == item["id"]:
                                    print("Alarma de máquina, Servo errorid", i,
                                        item["zh_CN"]["description"])
                                    break

                        choose = input("Introduzca 1 para borrar el error y permitir que la máquina continúe funcionando: ")
                        if int(choose) == 1:
                            dashboard.ClearError()
                            sleep(0.01)
                            dashboard.Continue()

            else:
                if int(enableStatus_robot) == 1 and int(algorithm_queue) == 0:
                    dashboard.Continue()
            globalLockValue.release()
            sleep(5) 
             
    def WaitArrive(point_list):
        while True:
            is_arrive = True
            globalLockValue.acquire()
            if current_actual is not None:
                for index in range(4):
                    if (abs(current_actual[index] - point_list[index]) > 1):
                        is_arrive = False
                if is_arrive:
                    globalLockValue.release()
                    return
            globalLockValue.release()
            sleep(0.001)
        
    def RunPoint(move: DobotApiMove, point_list: list):
        move.MovJ(point_list[0], point_list[1], point_list[2],
        point_list[3], point_list[4], point_list[5])
              
    def ConnectRobot():
        try:
            ip = "10.112.200.16"
            dashboardPort = 29999
            movePort = 30003
            feedPort = 30004
            print("Estableciendo conexión...")
            dashboard = DobotApiDashboard(ip, dashboardPort)
            move = DobotApiMove(ip, movePort)
            feed = DobotApi(ip, feedPort)
            feedFour = DobotApiFeedBack(ip,feedPort)
            print("Conexión establecida!...")
            return dashboard, move, feed,feedFour, ip
        except Exception as e:
            print(":(Conexión fallida:(")
            raise e


@dataclass
class Resultat:
    Error: int			#Sin error = 0, Con error = 1
    Param: List[float]	#tabla de parametros en reales. 
						#Normalmente, devuelve en Param[0] los valores
						

    @staticmethod
    def desc_resultat(texte: str) -> "Resultat":
        end = texte.index(",")
        error = int(texte[0:end])

        start = texte.index("{") + 1
        end = texte.index("}")
        str_parametros = texte[start:end]

        parametros = [float(c) for c in str_parametros.split(",") if c]
        return Resultat(error, parametros)      

