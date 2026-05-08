#!/bin/bash

# ==============================================================================
# Nombre del Script: config.sh
# Descripción: Plantilla para manejo de flags
# ==============================================================================

# Colores para mensajes (opcional, para mejor legibilidad)
VERDE='\033[0;32m'
NC='\033[0m' # Sin color
OPTIONS="slrh"

# Función de ayuda
mostrar_ayuda() {
    echo "Uso: $0 [-s] [-r] [-h]"
    echo ""
    echo "Opciones:"
    echo "  -s 	Configuración para simulador"
    echo "  -l 	Iniciar el simulador"
    echo "  -r 	Configuración para robot real"
    echo "  -h 	Muestra este mensaje de ayuda"
    exit 0
}

# Procesar los flags
while getopts $OPTIONS opt; do
    case ${opt} in
        s )
            [[ -z $MODO_SIM ]] && MODO_SIM=true
            ;;
		l )
            [[ -z $SIM_LAUNCH ]] && SIM_LAUNCH=true
			;;
        r )
            [[ -z $MODO_SIM ]] && MODO_SIM=false
            ;;
        h )
            mostrar_ayuda
            ;;
        \? )
			echo
            mostrar_ayuda
            ;;
    esac
done

[[ -z "$MODO_SIM" ]] && exit 0

if "$MODO_SIM"; then
    source /home/$(whoami)/turtlebot3_ws/install/setup.bash
	export TURTLEBOT3_MODEL=burger
	echo "sim"
else
    echo "real"
fi

if [[ -n "$SIM_LAUNCH" ]]; then
	ros2 launch turtlebot3_gazebo turtlebot3_laberint.launch.py
fi
