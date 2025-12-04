from collections import deque, defaultdict
import math

# 1. Definición del grafo del caso


def crear_grafo_universidad():
    """
    Grafo no dirigido de la universidad.
    Los pesos representan minutos en ascensor entre ubicaciones.
    Nodos:
        - Z10: Zona de descanso (planta 10) – PISTA 3
        - F7:  Despacho de Fausto (planta 7) – PISTA 2
        - B6:  Biblioteca (planta 6)
        - A3:  Aulas grandes (planta 3)
        - C0:  Cafetería (planta 0)
        - S-1: Sótano – Taller 3D – PISTA 1 y PISTA 4
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



# 2. Pistas y sospechosos

def crear_pistas():
    """
    Modelamos cada pista como un diccionario con:
        - id: código de pista
        - lugar: nodo del grafo donde se encuentra
        - descripcion: texto breve
        - sospechosos: diccionario {nombre_sospechoso: peso_de_evidencia}
          (peso alto = evidencia fuerte, peso bajo = evidencia débil)
    """
    pistas = [
        {
            "id": "P1",
            "lugar": "S-1",
            "descripcion": "Fragmento de script 'fix_impresora_pepelu.py' que activa el motor de la impresora 3D.",
            "sospechosos": {"Pepelu": 3}
        },
        {
            "id": "P2",
            "lugar": "F7",
            "descripcion": "Registro de tarjeta de Eva a las 19:52h en la planta 7.",
            "sospechosos": {"Eva": 3}
        },
        {
            "id": "P3",
            "lugar": "Z10",
            "descripcion": "Post-it: 'A las 20:00 todos al sótano. Traed sillas que hay Champions. —B.'",
            "sospechosos": {"Beltrán": 1}  # Pista cómica, evidencia débil
        },
        {
            "id": "P4",
            "lugar": "S-1",
            "descripcion": "Etiquetas del Black Friday de Zara en la papelera'.",
            "sospechosos": {"Adriana": 1}   # Pista cómica, evidencia débil
        },
       
        {
            "id": "P5",
            "lugar": "F7",
            "descripcion": "Restos de cera y prismáticos cerca del despacho de Fausto.",
            "sospechosos": {"Rodrigo": 2}  
        }
    ]
    return pistas


def agrupar_pistas_por_lugar(pistas):
    """
    Devuelve un diccionario:
        {nodo: [lista de pistas en ese nodo]}
    para poder consultarlo rápidamente durante el BFS.
    """
    por_lugar = defaultdict(list)
    for p in pistas:
        por_lugar[p["lugar"]].append(p)
    return por_lugar


# 3. BFS para explorar el grafo

def bfs_explorar(grafo, nodo_inicial, pistas_por_lugar):
    """
    Realiza un recorrido BFS a partir de 'nodo_inicial'.
    Devuelve:
        - orden_visita: lista con el orden en que se visitan los nodos
        - pistas_encontradas: lista de pistas (diccionarios) encontradas
          al ir pasando por los nodos.

    Complejidad temporal: O(V + E)
    Complejidad espacial: O(V)
    """
    visitados = set()
    cola = deque()
    orden_visita = []
    pistas_encontradas = []

    visitados.add(nodo_inicial)
    cola.append(nodo_inicial)

    while cola:
        actual = cola.popleft()
        orden_visita.append(actual)

        # ¿Hay pistas en este nodo?
        if actual in pistas_por_lugar:
            pistas_encontradas.extend(pistas_por_lugar[actual])

        # Exploramos vecinos
        for vecino, peso in grafo[actual]:
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append(vecino)

    return orden_visita, pistas_encontradas


# 4. Algoritmo de Dijkstra para rutas mínimas


def dijkstra(grafo, origen):
    """
    Implementación clásica de Dijkstra para grafos con pesos.

    Devuelve:
        - dist: diccionario {nodo: distancia mínima desde 'origen'}
        - previo: diccionario {nodo: nodo_anterior_en_el_camino}

    Complejidad temporal aproximada:
        O((V + E) log V) si se usa cola de prioridad
        En esta versión simple (sin heap) nos quedamos en O(V^2),
        suficiente para un grafo pequeño como este.
    """
    dist = {nodo: math.inf for nodo in grafo}
    previo = {nodo: None for nodo in grafo}
    dist[origen] = 0

    no_visitados = set(grafo.keys())

    while no_visitados:
        # Elegimos el nodo no visitado con menor distancia provisional
        actual = min(no_visitados, key=lambda n: dist[n])
        no_visitados.remove(actual)

        # Relajación de aristas
        for vecino, peso in grafo[actual]:
            nueva_dist = dist[actual] + peso
            if nueva_dist < dist[vecino]:
                dist[vecino] = nueva_dist
                previo[vecino] = actual

    return dist, previo


def reconstruir_camino(previo, origen, destino):
    """
    Reconstruye el camino mínimo desde 'origen' hasta 'destino'
    usando el diccionario 'previo' obtenido con Dijkstra.
    """
    camino = []
    actual = destino
    while actual is not None:
        camino.append(actual)
        if actual == origen:
            break
        actual = previo[actual]
    camino.reverse()
    return camino


# 5. Sistema de puntuación de sospechosos

def calcular_puntuaciones_sospechosos(pistas_encontradas):
    """
    A partir de una lista de pistas encontradas (diccionarios),
    suma los pesos de evidencia para cada sospechoso.

    Devuelve un diccionario:
        {nombre_sospechoso: puntuacion_total}
    """
    puntuaciones = defaultdict(int)

    for pista in pistas_encontradas:
        for sospechoso, peso in pista["sospechosos"].items():
            puntuaciones[sospechoso] += peso

    return dict(puntuaciones)


def ranking_sospechosos(puntuaciones):
    """
    Devuelve una lista de (sospechoso, puntuacion) ordenada
    de mayor a menor puntuación.
    """
    return sorted(puntuaciones.items(), key=lambda x: x[1], reverse=True)


# 6. Ejemplo de ejecución


if __name__ == "__main__":
    # Crear grafo y pistas
    grafo = crear_grafo_universidad()
    pistas = crear_pistas()
    pistas_por_lugar = agrupar_pistas_por_lugar(pistas)

    # 1) BFS desde la cafetería C0 (punto de partida de los alumnos)
    origen = "C0"
    orden, pistas_encontradas = bfs_explorar(grafo, origen, pistas_por_lugar)

    print("Orden de visita (BFS) comenzando en", origen, ":", orden)
    print("\nPistas encontradas:")
    for p in pistas_encontradas:
        print(f"- {p['id']} en {p['lugar']}: {p['descripcion']}")

    # 2) Dijkstra: tiempos mínimos desde la cafetería a todos los nodos
    dist, previo = dijkstra(grafo, origen)
    print("\nTiempos mínimos (minutos en ascensor) desde", origen, ":")
    for nodo in grafo:
        print(f"- Hasta {nodo}: {dist[nodo]} minutos")

    # Ejemplo: camino mínimo desde C0 hasta el sótano S-1
    camino_c0_sotano = reconstruir_camino(previo, "C0", "S-1")
    print("\nCamino mínimo de C0 a S-1:", " -> ".join(camino_c0_sotano),
          f"({dist['S-1']} minutos)")

    # 3) Puntuación de sospechosos según las pistas encontradas
    puntuaciones = calcular_puntuaciones_sospechosos(pistas_encontradas)
    ranking = ranking_sospechosos(puntuaciones)

    print("\nPuntuación de sospechosos:")
    for sospechoso, puntos in ranking:
        print(f"- {sospechoso}: {puntos} puntos")

    # En este diseño deberían salir en cabeza Pepelu y Eva