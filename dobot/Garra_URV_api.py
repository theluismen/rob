#from dobot_api import DobotApiDashboard, DobotApi, DobotApiMove, MyType
from Utils_URV_Nova_api import Resultat
import time


def Sleep(ms):
    time.sleep(ms / 1000.0)



class Gripper:
    
    MIN_APERTURA = 0
    MAX_APERTURA = 1000
    MAX_FORCE = 100
    MIN_FORCE = 20
    MAX_SPEED = 100
    MIN_SPEED = 1	
	
    def __init__(self, dashboard, move, ip):
        self._move= move
        self._dashboard= dashboard
        self._modbus_id = None
        self._ip = ip
        self.iniciar_modbus(self._ip)
        self.init_garra()
        self.set_force(30)
        self.set_speed(50)
        print("Griper connectat...")
        
# ---------- gestión Modbus --------------------------

    def iniciar_modbus(self, _ip):
        #cierro el moodbus 1 por si ha quedado abierto por error de ejecución anterior
        self._dashboard.ModbusClose(1) 
        
        #llamo a crear Modbus y me devolverá modbus_id = 1
        resul = Resultat.desc_resultat(
            self._dashboard.ModbusCreate(_ip, 60000, 1, True)
        )

        if resul.Error != 0:
            print("Create failed:", resul.Error)
            raise ValueError("No se ha podido crear la conexión de Modbus")
        self._modbus_id = int(resul.Param[0])

    def cerrar_modbus(self):
        if self._modbus_id is not None:
            self._dashboard.ModbusClose(self._modbus_id)
            self._modbus_id = None

# ---------- inicialización pinza ------------------

    def init_garra(self):
        if self._modbus_id is None:
            raise RuntimeError("Modbus no inicializado")
        self._dashboard.SetHoldRegs(self._modbus_id, 256, 1, "{165}", "U16")
        while True:
            data1 = Resultat.desc_resultat(
                self._dashboard.GetHoldRegs(self._modbus_id, 512, 1, "U16")
            )
            Sleep(500)
            if int(data1.Param[0]) == 1:
                break
        print("Inicialización de la pinza DH completada...\r\n")

# ---------- lecturas de fuerza y posición ----------

    def get_force(self) :
        data2 = Resultat.desc_resultat(
            self._dashboard.GetHoldRegs(self._modbus_id, 257, 1, "U16")
        )
        return (data2.Param[0])

    def get_position(self) :
        data2 = Resultat.desc_resultat(
            self._dashboard.GetHoldRegs(self._modbus_id, 514, 1, "U16")
        )
        return (data2.Param[0])

# ---------- escritura de fuerza, posición y velocidad ----------

    def set_force(self, force: int):
# La función comprueba el parámetro de fuerza, y si está en los límites lo actualiza.
# Si está por debajo de limite, lo actualiza con fuerza mínima.
# Si está por encima de límite, lo actualiza con fuerza máxima.
        if force < self.MIN_FORCE:
            print(
                f"Fuerza={force} < {self.MIN_FORCE}. "
                "Asignamos Fuerza mínima."
            )
            force = self.MIN_FORCE
        elif force > self.MAX_FORCE:
            print(
                f"Fuerza={force} > {self.MAX_FORCE}. "
                "Asignamos Fuerza máxima."
            )
            force = self.MAX_FORCE

        self._dashboard.SetHoldRegs(
            self._modbus_id, 257, 1, f"{force}", "U16"
        )
#       print(f"Actualización de Fuerza={force} completada...\r\n")

    def set_speed(self, speed: int):
# La función comprueba el parámetro de velocidad, y si está en los límites lo actualiza.
# Si está por debajo de limite, lo actualiza con velocidad mínima.
# Si está por encima de límite, lo actualiza con valocidad máxima.
        if speed < self.MIN_SPEED:
            print(
                f"Velocidad={speed} < {self.MIN_SPEED}. "
                "Asignamos Velocidad mínima."
            )
            speed = self.MIN_SPEED
        elif speed > self.MAX_SPEED:
            print(
                f"Velocidad={speed} > {self.MAX_SPEED}. "
                "Asignamos Velocidad máxima."
            )
            speed = self.MAX_SPEED

        self._dashboard.SetHoldRegs(
            self._modbus_id, 260, 1, f"{speed}", "U16"
        )
#       print(f"Actualización de Velocidad={speed} completada...\r\n")


    def set_position(self, apertura: int):
# La función comprueba el parámetro de apertura, y si está en los límites lo actualiza.
# Si está por debajo de limite, lo actualiza con apertura mínima.
# Si está por encima de límite, lo actualiza con apertura máxima.
        if apertura < self.MIN_APERTURA:
            print(
                f"Apertura={apertura} < {self.MIN_APERTURA}. "
                "Asignamos Apertura mínima."
            )
            apertura = self.MIN_APERTURA
        elif apertura > self.MAX_APERTURA:
            print(
                f"Apertura={apertura} > {self.MAX_APERTURA}. "
                "Asignamos Apertura máxima."
            )
            apertura = self.MAX_APERTURA

#		actualización de la apertura
        self._dashboard.SetHoldRegs(
            self._modbus_id, 259, 1, f"{apertura}", "U16"
        )
        Sleep(100)
#		espera de la actualización de la apertura        
        while True:
            data_open = Resultat.desc_resultat(
                self._dashboard.GetHoldRegs(self._modbus_id, 513, 1, "U16")
            )
            Sleep(100)
            if int(data_open.Param[0]) in (1, 2):
                break

#       print(f"Actualización de apertura a={apertura} completada...\r\n")
#		devuelve si la pinza ha llegado a la posición de referencia (return = 1)
        return (int(data_open.Param[0]))

# ---------- operaciones abrir/cerrar ------------------

    def Open(self):
# La función abre la garra al máximo.
        self._move.Sync()
        self._dashboard.SetHoldRegs(
            self._modbus_id, 259, 1, "{1000}", "U16"
        )
        Sleep(200)
        while True:
            data_open = Resultat.desc_resultat(
                self._dashboard.GetHoldRegs(self._modbus_id, 513, 1, "U16")
            )
            Sleep(100)
            if int(data_open.Param[0]) in (1, 2):
                break
        self._move.Sync()
        Sleep(1000)

#       print("Apertura de la pinza DH completada...\r\n")
#		devuelve si la pinza ha llegado a la posición máxima (return = 1)
        return (int(data_open.Param[0]))

    def Close(self):
# La función cierra la garra al máximo.
        self._move.Sync()
        self._dashboard.SetHoldRegs(
            self._modbus_id, 259, 1, "{0}", "U16"
        )
        Sleep(200)
        while True:
            data_close = Resultat.desc_resultat(
                self._dashboard.GetHoldRegs(self._modbus_id, 513, 1, "U16")
            )
            Sleep(100)
            if int(data_close.Param[0]) in (1, 2):
                break
        self._move.Sync()
        Sleep(1000)
#		devuelve si la pinza ha llegado a la posición mínima (return = 1)
#		o si no consigue llegar, por que lleva un opbjeto (return = 2)
        return (int(data_close.Param[0]))

