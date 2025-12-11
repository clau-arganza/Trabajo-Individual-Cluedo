from collections import deque, defaultdict
import math
import matplotlib.pyplot as plt
import time  # para la cuenta atrás

# 1. Grafo del caso

def crear_grafo_universidad():
    """
    Grafo no dirigido de la universidad.
    Los pesos representan minutos en ascensor entre ubicaciones.

    Nodos y pistas:
      - Z10: Zona de descanso (planta 10) – P3 (Beltrán)
      - F7:  Despacho de Fausto (planta 7) – P2 (Eva)
      - B6:  Biblioteca (planta 6) – P5 (Rodrigo)
      - A3:  Aulas grandes (planta 3) – P4 (Adriana)
      - C0:  Cafetería (planta 0) – sin pistas
      - S-1: Sótano / taller 3D – P1 (Pepelu)
    """
    grafo = {
        "Z10": [("F7", 5), ("B6", 6), ("A3", 9), ("C0", 12), ("S-1", 13)],
        "F7":  [("Z10", 5), ("B6", 3), ("A3", 6), ("C0", 9), ("S-1", 10)],
        "B6":  [("Z10", 6), ("F7", 3), ("A3", 5), ("C0", 8), ("S-1", 9)],
        "A3":  [("Z10", 9), ("F7", 6), ("B6", 5), ("C0", 5), ("S-1", 6)],
        "C0":  [("Z10", 12), ("F7", 9), ("B6", 8), ("A3", 5), ("S-1", 3)],
        "S-1": [("Z10", 13), ("F7", 10), ("B6", 9), ("A3", 6), ("C0", 3)],
    }
    return grafo


# POSICIONES DEL GRAFO

POSICIONES = {
    "Z10": (0, 10),
    "F7":  (-1, 8),
    "B6":  (1, 6),
    "A3":  (-1, 4),
    "C0":  (1, 2),
    "S-1": (0, 0),
}


# 2. Grafo base

def dibujar_grafo_base(grafo):
    plt.figure(figsize=(5, 10))

    for nodo, (x, y) in POSICIONES.items():
        plt.scatter(x, y, s=2000)
        plt.text(x, y, nodo, ha="center", va="center",
                 color="white", fontsize=12)

    dibujadas = set()
    for origen, vecinos in grafo.items():
        x1, y1 = POSICIONES[origen]
        for destino, peso in vecinos:
            if (destino, origen) in dibujadas:
                continue
            dibujadas.add((origen, destino))
            x2, y2 = POSICIONES[destino]
            plt.plot([x1, x2], [y1, y2])
            xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
            plt.text(
                xm, ym, str(peso),
                fontsize=9, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.2",
                          fc="white", ec="none")
            )

    plt.title("Grafo del edificio (minutos en ascensor)")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


# 3. Grafo con pistas

def dibujar_grafo_con_pistas(grafo, pistas_por_lugar):
    plt.figure(figsize=(6, 10))

    for nodo, (x, y) in POSICIONES.items():
        plt.scatter(x, y, s=2000)
        plt.text(x, y + 0.3, nodo, ha="center", va="center",
                 color="white", fontsize=12, fontweight="bold")

        if nodo in pistas_por_lugar:
            ids = ", ".join(p["id"] for p in pistas_por_lugar[nodo])
            texto = f"Pistas: {ids}"
        else:
            texto = "Sin pistas"

        plt.text(x, y - 0.8, texto, ha="center", va="center", fontsize=9)

    dibujadas = set()
    for origen, vecinos in grafo.items():
        x1, y1 = POSICIONES[origen]
        for destino, peso in vecinos:
            if (destino, origen) in dibujadas:
                continue
            dibujadas.add((origen, destino))
            x2, y2 = POSICIONES[destino]
            plt.plot([x1, x2], [y1, y2])
            xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
            plt.text(
                xm, ym, str(peso),
                fontsize=8, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.2",
                          fc="white", ec="none")
            )

    plt.title("Grafo con pistas por nodo")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


# 4. Grafo con sospechoso principal por nodo

def dibujar_grafo_con_sospechosos(grafo, pistas_por_lugar):
    plt.figure(figsize=(6, 10))

    for nodo, (x, y) in POSICIONES.items():
        plt.scatter(x, y, s=2500)
        plt.text(x, y + 0.6, nodo, ha="center", va="center",
                 color="white", fontsize=12, fontweight="bold")

        texto = "Sin sospechosos"
        if nodo in pistas_por_lugar:
            puntos_locales = defaultdict(int)
            for pista in pistas_por_lugar[nodo]:
                for sospechoso, peso in pista["sospechosos"].items():
                    puntos_locales[sospechoso] += peso

            if puntos_locales:
                sospechoso_top, puntos_top = max(
                    puntos_locales.items(), key=lambda x: x[1]
                )
                texto = f"{sospechoso_top} ({puntos_top} pts)"

        plt.text(x, y - 0.4, texto, ha="center", va="center",
                 fontsize=10, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3",
                           fc="white", ec="black"))

    dibujadas = set()
    for origen, vecinos in grafo.items():
        x1, y1 = POSICIONES[origen]
        for destino, _ in vecinos:
            if (destino, origen) in dibujadas:
                continue
            dibujadas.add((origen, destino))
            x2, y2 = POSICIONES[destino]
            plt.plot([x1, x2], [y1, y2], linestyle="--", color="gray")

    plt.title("Sospechoso principal por nodo")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


# 5. Pistas del caso

def crear_pistas():
    pistas = [
        {
            "id": "P1",
            "lugar": "S-1",  # Pepelu -> sótano
            "descripcion": "Fragmento de script 'fix_impresora_pepelu.py' que activa el motor de la impresora 3D",
            "sospechosos": {"Pepelu": 4}
        },
        {
            "id": "P2",
            "lugar": "F7",  # Eva -> despacho Fausto
            "descripcion": "Registro de tarjeta de Eva a las 19:52h en la planta 7",
            "sospechosos": {"Eva": 4}
        },
        {
            "id": "P3",
            "lugar": "Z10",  # Beltrán -> post-it
            "descripcion": "Post-it: 'A las 20:00 todos al sótano. Traed sillas que hay Champions. —B.",
            "sospechosos": {"Beltrán": 1}
        },
        {
            "id": "P4",
            "lugar": "A3",  # Adriana -> aulas grandes
            "descripcion": "Etiquetas del Black Friday de Zara en la papelera de la clase que había dado Fausto la hora anterior a su muerte",
            "sospechosos": {"Adriana": 2}
        },
        {
            "id": "P5",
            "lugar": "B6",  # Rodrigo -> biblioteca
            "descripcion": "Restos de cera y prismáticos al lado del casco de moto de Fausto",
            "sospechosos": {"Rodrigo": 3}
        },
    ]
    return pistas


def agrupar_pistas_por_lugar(pistas):
    por_lugar = defaultdict(list)
    for p in pistas:
        por_lugar[p["lugar"]].append(p)
    return por_lugar


# 6. BFS

def bfs_explorar(grafo, nodo_inicial, pistas_por_lugar):
    visitados = set([nodo_inicial])
    cola = deque([nodo_inicial])
    orden = []
    pistas_encontradas = []

    while cola:
        actual = cola.popleft()
        orden.append(actual)

        if actual in pistas_por_lugar:
            pistas_encontradas.extend(pistas_por_lugar[actual])

        for vecino, _ in grafo[actual]:
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append(vecino)

    return orden, pistas_encontradas


# 7. Dijkstra

def dijkstra(grafo, origen):
    dist = {n: math.inf for n in grafo}
    previo = {n: None for n in grafo}
    dist[origen] = 0
    no_visitados = set(grafo.keys())

    while no_visitados:
        actual = min(no_visitados, key=lambda n: dist[n])
        no_visitados.remove(actual)

        for vecino, peso in grafo[actual]:
            nueva = dist[actual] + peso
            if nueva < dist[vecino]:
                dist[vecino] = nueva
                previo[vecino] = actual

    return dist, previo


def reconstruir_camino(previo, origen, destino):
    camino = []
    actual = destino
    while actual is not None:
        camino.append(actual)
        if actual == origen:
            break
        actual = previo[actual]
    return camino[::-1]

# 8.bis Distancias entre todos los nodos + plan óptimo

def precomputar_distancias_todas(grafo):
    distancias = {}
    for o in grafo:
        dist, _ = dijkstra(grafo, o)
        distancias[o] = dist
    return distancias


def valor_lugar(lugar, pistas_por_lugar):
    total = 0
    for p in pistas_por_lugar.get(lugar, []):
        total += sum(p["sospechosos"].values())
    return total


def mejor_ruta_investigacion(origen, t_max, pistas_por_lugar, distancias):
    valor_por_lugar = {l: valor_lugar(l, pistas_por_lugar) for l in distancias}

    mejor_val = -1
    mejor_cam = [origen]

    def backtracking(actual, tiempo, valor, visitados, camino):
        nonlocal mejor_val, mejor_cam

        if valor > mejor_val:
            mejor_val = valor
            mejor_cam = list(camino)

        for sig in distancias[actual]:
            if sig == actual:
                continue
            coste = distancias[actual][sig]
            if tiempo + coste > t_max:
                continue

            ganancia = valor_por_lugar[sig] if sig not in visitados else 0

            camino.append(sig)
            backtracking(sig, tiempo + coste, valor + ganancia,
                         visitados | {sig}, camino)
            camino.pop()

    v0 = valor_lugar(origen, pistas_por_lugar)
    visit0 = {origen} if v0 > 0 else set()

    backtracking(origen, 0, v0, visit0, [origen])

    return mejor_val, mejor_cam

# 9. Puntuación de sospechosos

def calcular_puntuaciones_sospechosos(pistas_encontradas):
    punt = defaultdict(int)
    for pista in pistas_encontradas:
        for sospechoso, peso in pista["sospechosos"].items():
            punt[sospechoso] += peso
    return dict(punt)


def ranking_sospechosos(puntuaciones):
    return sorted(puntuaciones.items(), key=lambda x: x[1], reverse=True)


# 10. PROGRAMA PRINCIPAL (MENÚ)

if __name__ == "__main__":
    grafo = crear_grafo_universidad()
    pistas = crear_pistas()
    pistas_por_lugar = agrupar_pistas_por_lugar(pistas)
    origen = "C0"
    distancias_todas = precomputar_distancias_todas(grafo)

    print("=== CLUEDO FINAL ===")  # para comprobar que es este archivo

    print("Pistas por lugar:",
          {k: [p['id'] for p in v] for k, v in pistas_por_lugar.items()})
    
    while True:
        print("\n============================")
        print("¿Qué quieres ver ahora?")
        print("1) Grafo base + BFS + Dijkstra + ranking sospechosos")
        print("2) Grafo con pistas en cada nodo")
        print("3) Plan óptimo de investigación (tiempo limitado)")
        print("4) Grafo con sospechoso principal por nodo")
        print("5) ¿Quieres saber quién fue el asesino?")
        print("============================")
        modo = input("Elige 1, 2, 3, 4 o 5: ").strip()

        if modo == "1":
            dibujar_grafo_base(grafo)

            orden, pistas_encontradas = bfs_explorar(grafo, origen, pistas_por_lugar)
            print("\nOrden BFS:", orden)

            print("\nPistas encontradas:")
            for p in pistas_encontradas:
                print(f"- {p['id']} ({p['descripcion']}) en {p['lugar']}")

            dist, prev = dijkstra(grafo, origen)
            print("\nTiempos mínimos desde", origen)
            for n in grafo:
                print(f"- {n}: {dist[n]} min")

            camino = reconstruir_camino(prev, origen, "S-1")
            print("\nCamino mínimo C0 → S-1:", " -> ".join(camino),
                  f"({dist['S-1']} min)")

            puntuaciones = calcular_puntuaciones_sospechosos(pistas_encontradas)
            ranking = ranking_sospechosos(puntuaciones)

            print("\nRanking sospechosos (global):")
            for s, pts in ranking:
                print(f"- {s}: {pts} puntos")

        elif modo == "2":
            dibujar_grafo_con_pistas(grafo, pistas_por_lugar)

        elif modo == "3":
            print("\n=== PLAN ÓPTIMO DE INVESTIGACIÓN ===")
            try:
                t_max = int(input("¿Cuántos minutos tiene el inspector? "))
            except ValueError:
                print("Tiempo no válido.")
                continue

            mejor_valor, mejor_camino = mejor_ruta_investigacion(
                origen, t_max, pistas_por_lugar, distancias_todas
            )

            print(f"\nRuta óptima en ≤ {t_max} minutos:")
            print(" -> ".join(mejor_camino))
            print(f"Valor total de información recogida: {mejor_valor} puntos")

        elif modo == "4":
            # AQUÍ va el grafo de sospechosos, no el asesino final
            dibujar_grafo_con_sospechosos(grafo, pistas_por_lugar)

        elif modo == "5":
            # AQUÍ va la revelación del asesino
            print("\nHas elegido la opción 5.")
            r = input("¿Quieres saber quiénes fueron los asesinos? (si/no): ").strip().lower()

            for n in [3, 2, 1]:
                print(n)
                time.sleep(1)

            if r.startswith("s"):
                print("\nLos verdaderos asesinos fueron... PEPELU Y EVA!!!")
                print("Eva no soportaba más las cuentas atrás de Fausto y")
                print("Pepelu se compinchó por celos.")
            else:
                print("\nTú mismo, te quedas sin saberlo.")

            print("\nFin del programa. ¡Hasta pronto!")
            break

        else:
            print("Opción no válida.")