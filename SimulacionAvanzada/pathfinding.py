# Rutas para la estrategia mejorada.
# La PriorityQueue, to_int y dijkstra salen del notebook Path Planning.ipynb
# del profe. Lo unico que cambia es get_neighborhood: el suyo solo revisa que
# la celda caiga dentro del tablero, y aqui ademas hay que preguntarle a
# puede_pasar si hay una pared o una puerta cerrada de por medio.
import heapq

from paredes import puede_pasar, celda_vecina

INFINITE = 1_000_000


class PriorityQueue:
    def __init__(self):
        self.__data = []

    def empty(self):
        return not self.__data

    def push(self, priority, value):
        heapq.heappush(self.__data, (priority, value))

    def pop(self):
        if self.__data:
            heapq.heappop(self.__data)
        else:
            raise Exception("No such element")

    def top(self):
        if self.__data:
            return self.__data[0]
        else:
            raise Exception("No such element")


def to_int(matrix, position):
    (row, col) = position
    cols = len(matrix[0])
    return (row * cols) + col


def get_neighborhood(model, position):
    result = []
    (row, col) = position
    for direccion in range(4):
        if puede_pasar(model, row, col, direccion):
            result.append(celda_vecina(row, col, direccion))
    return result


def costos(model, cargando):
    # matriz de costos de la casa. -1 es celda por la que no se puede pasar
    matrix = []
    for fila in range(6):
        renglon = []
        for col in range(8):
            costo = 1
            if model.fuego[fila][col] == 1:
                costo = 2                  # el humo estorba pero se cruza
            if model.fuego[fila][col] == 2:
                costo = 5                  # el fuego se rodea si hay por donde
                if cargando:
                    costo = -1             # con una victima encima ni se intenta
            renglon.append(costo)
        matrix.append(renglon)
    return matrix


def dijkstra(model, matrix, src, dest):
    n = len(matrix) * len(matrix[0])
    dist = [INFINITE] * n
    prev = [None] * n
    pq = PriorityQueue()

    dist[to_int(matrix, src)] = 0
    pq.push(0, src)
    while not pq.empty():
        (current_dist, u) = pq.top()
        pq.pop()

        if u == dest:
            break

        for v in get_neighborhood(model, u):
            (row, col) = v
            if matrix[row][col] != -1:
                new_dist = dist[to_int(matrix, u)] + matrix[row][col]

                if new_dist < dist[to_int(matrix, v)]:
                    dist[to_int(matrix, v)] = new_dist
                    prev[to_int(matrix, v)] = u
                    pq.push(new_dist, v)

    # reconstruir el camino
    path = []
    u = dest
    if prev[to_int(matrix, u)] is not None or u == src:
        while u is not None:
            path.insert(0, u)
            u = prev[to_int(matrix, u)]

    return dist[to_int(matrix, dest)], path
