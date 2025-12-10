from collections import deque, defaultdict
import math
import matplotlib.pyplot as plt
import time  # para la cuenta atrás

# ============================================================
# 1. Grafo del caso
# ============================================================

def crear_grafo_universidad():
    grafo = {
        "Z10": [("F7", 5), ("B6", 6), ("A3", 9), ("C0", 12), ("S-1", 13)],
        "F7":  [("Z10", 5), ("B6", 3), ("A3", 6), ("C0", 9), ("S-1", 10)],
        "B6":  [("Z10", 6), ("F7", 3), ("A3", 5), ("C0", 8), ("S-1", 9)],
        "A3":  [("Z10", 9), ("F7", 6), ("B6", 5), ("C0", 5), ("S-1", 6)],
        "C0":  [("Z10", 12), ("F7", 9), ("B6", 8), ("A3", 5), ("S-1", 3)],
        "S-1": [("Z10", 13), ("F7", 10), ("B6", 9), ("A3", 6), ("C0", 3)],
    }
    return grafo


POSICIONES = {
    "Z10": (0, 10),
    "F7":  (-1, 8),
    "B6":  (1, 6),
    "A3":  (-1, 4),
    "C0":  (1, 2),
    "S-1": (0, 0),
}


# ============================================================
# 2. Dibujar grafo base
# ============================================================

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
            plt.text(xm, ym, str(peso), fontsize=9, ha="center")

    plt.title("Grafo del edificio (minutos en ascensor)")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


# ============================================================
# 3. Grafo con pistas
# ============================================================

def dibujar_grafo_con_pistas(grafo, pistas_por_lugar):
    plt.figure(figsize=(6, 10))

    for nodo, (x, y) in POSICIONES.items():
        plt.scatter(x, y, s=2000)
        plt.text(x, y + 0.3, nodo, ha="center",
                 color="white", fontsize=12, fontweight="bold")

        if nodo in pistas_por_lugar:
            ids = ", ".join(p["id"] for p in pistas_por_lugar[nodo])
            texto = f"Pistas: {ids}"
        else:
            texto = "Sin pistas"

        plt.text(x, y - 0.8, texto, ha="center", fontsize=9)

    # aristas
    dib = set()
    for o, vecinos in grafo.items():
        x1, y1 = POSICIONES[o]
        for d, peso in vecinos:
            if (d, o) in dib:
                continue
            dib.add((o, d))
            x2, y2 = POSICIONES[d]
            plt.plot([x1, x2], [y1, y2])
            xm, ym = (x1 + x2)/2, (y1 + y2)/2
            plt.text(xm, ym, str(peso), fontsize=8, ha="center")

    plt.title("Grafo con pistas por nodo")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


# ============================================================
# 4. Grafo con sospechoso principal por nodo
# ============================================================

def dibujar_grafo_con_sospechosos(grafo, pistas_por_lugar):
    plt.figure(figsize=(6, 10))

    for nodo, (x, y) in POSICIONES.items():
        plt.scatter(x, y, s=2500)
        plt.text(x, y + 0.6, nodo, ha="center",
                 color="white", fontsize=12, fontweight="bold")

        texto = "Sin sospechosos"
        if nodo in pistas_por_lugar:
            puntos = defaultdict(int)
            for pista in pistas_por_lugar[nodo]:
                for s, peso in pista["sospechosos"].items():
                    puntos[s] += peso
            if puntos:
                top, pts = max(puntos.items(), key=lambda x: x[1])
                texto = f"{top} ({pts} pts)"

        plt.text(x, y - 0.4, texto, ha="center",
                 fontsize=10, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3",
                           fc="white", ec="black"))

    dib = set()
    for o, vecinos in grafo.items():
        x1, y1 = POSICIONES[o]
        for d, _ in vecinos:
            if (d, o) in dib:
                continue
            dib.add((o, d))
            x2, y2 = POSICIONES[d]
            plt.plot([x1, x2], [y1, y2], linestyle="--", color="gray")

    plt.title("Sospechoso principal por nodo")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


# ============================================================
# 5. Pistas
# ============================================================

def crear_pistas():
    return [
        {"id": "P1", "lugar": "S-1",
         "descripcion": "Script 3D de Pepelu",
         "sospechosos": {"Pepelu": 4}},
        {"id": "P2", "lugar": "F7",
         "descripcion": "Tarjeta de Eva a las 19:52",
         "sospechosos": {"Eva": 4}},
        {"id": "P3", "lugar": "Z10",
         "descripcion": "Post-it de Beltrán",
         "sospechosos": {"Beltrán": 1}},
        {"id": "P4", "lugar": "A3",
         "descripcion": "Etiquetas Zara de Adriana",
         "sospechosos": {"Adriana": 2}},
        {"id": "P5", "lugar": "B6",
         "descripcion": "Cera y prismáticos de Rodrigo",
         "sospechosos": {"Rodrigo": 3}},
    ]

def agrupar_pistas_por_lugar(pistas):
    d = defaultdict(list)
    for p in pistas:
        d[p["lugar"]].append(p)
    return d


# ============================================================
# 6. BFS
# ============================================================

def bfs_explorar(grafo, inicio, pistas_por_lugar):
    visitados = {inicio}
    cola = deque([inicio])
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


# ============================================================
# 7. Dijkstra + camino
# ============================================================

def dijkstra(grafo, origen):
    dist = {n: math.inf for n in grafo}
    prev = {n: None for n in grafo}
    dist[origen] = 0
    no_visit = set(grafo.keys())

    while no_visit:
        actual = min(no_visit, key=lambda n: dist[n])
        no_visit.remove(actual)

        for vecino, peso in grafo[actual]:
            nueva = dist[actual] + peso
            if nueva < dist[vecino]:
                dist[vecino] = nueva
                prev[vecino] = actual

    return dist, prev


def reconstruir_camino(prev, origen, destino):
    camino = []
    actual = destino
    while actual is not None:
        camino.append(actual)
        if actual == origen:
            break
        actual = prev[actual]
    return camino[::-1]


# ============================================================
# 7 BIS. Distancias entre todas las parejas + plan óptimo
# ============================================================

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
    valor_por_lugar = {
        lugar: valor_lugar(lugar, pistas_por_lugar)
        for lugar in distancias
    }

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
            t2 = tiempo + coste
            if t2 > t_max:
                continue

            ganancia = valor_por_lugar[sig] if sig not in visitados else 0

            camino.append(sig)
            backtracking(sig, t2, valor + ganancia,
                         visitados | {sig}, camino)
            camino.pop()

    v0 = valor_lugar(origen, pistas_por_lugar)
    visit0 = {origen} if v0 > 0 else set()

    backtracking(origen, 0, v0, visit0, [origen])

    return mejor_val, mejor_cam


# ============================================================
# 8. Ranking sospechosos
# ============================================================

def calcular_puntuaciones_sospechosos(pistas_encontradas):
    punt = defaultdict(int)
    for p in pistas_encontradas:
        for s, peso in p["sospechosos"].items():
            punt[s] += peso
    return dict(punt)


def ranking_sospechosos(puntuaciones):
    return sorted(puntuaciones.items(), key=lambda x: x[1], reverse=True)


# ============================================================
# 9. MENÚ PRINCIPAL
# ============================================================

if __name__ == "__main__":
    grafo = crear_grafo_universidad()
    pistas = crear_pistas()
    pistas_por_lugar = agrupar_pistas_por_lugar(pistas)
    origen = "C0"
    distancias_todas = precomputar_distancias_todas(grafo)

    print("=== CLUEDO FINAL ===")

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

        # ---- 1 ----
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

        # ---- 2 ----
        elif modo == "2":
            dibujar_grafo_con_pistas(grafo, pistas_por_lugar)

        # ---- 3 (nuevo algoritmo de optimización) ----
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

        # ---- 4 ----
        elif modo == "4":
            dibujar_grafo_con_sospechosos(grafo, pistas_por_lugar)

        # ---- 5 ----
        elif modo == "5":
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
