def mostrar_torres(torres):
    print("\nEstado actual:")
    for nombre, torre in torres.items():
        print(f"{nombre}: {torre}")


def mover_disco(torres, alturas, origen, destino):

    altura_origen = alturas[origen]
    altura_destino = alturas[destino]

    disco = torres[origen].pop()

    print(
        f"Mover disco {disco} "
        f"de {origen}[altura {(altura_origen)*15.0}] "
        f"a {destino}[altura {(altura_destino)*15.0}]"
    )

    torres[destino].append(disco)

    alturas[origen] -= 1
    alturas[destino] += 1

def hanoi(n, origen, destino, auxiliar, torres, alturas):
    if n == 1:
        mover_disco(torres, alturas, origen, destino)
        return

    hanoi(n - 1, origen, auxiliar, destino, torres, alturas)

    mover_disco(torres, alturas, origen, destino)

    hanoi(n - 1, auxiliar, destino, origen, torres, alturas)


# -------------------------
# Programa principal
# -------------------------

n = 3

torres = {
    "A": [3, 2, 1],
    "B": [],
    "C": []
}

alturas = {
    "A": 3,
    "B": 1,
    "C": 1
}

mostrar_torres(torres)
mostrar_torres(alturas)

hanoi(n, "A", "C", "B", torres, alturas)

mostrar_torres(torres)
mostrar_torres(alturas)
