# Requiero Mesa > 3.3
# Modelo de Flash Point Fire Rescue, reglas del Family Game Setup.
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

import numpy as np

# archivos del equipo. ninguno de ellos importa a este, para no hacer un circulo
from tablero import leer_tab
from paredes import celda_vecina
from poi import crear_bolsa, reponer_poi
from fuego import avanzar_fuego, flashover, efectos_secundarios
from bombero import Bombero
from bombero_mejorado import BomberoMejorado


def get_grid(model):
    grid = np.zeros((model.grid.width, model.grid.height))
    for content, (x, y) in model.grid.coord_iter():
        # el grid de mesa va (columna, fila) y nuestras capas van [fila][columna]
        if model.fuego[y][x] == 1:
            grid[x][y] = 1                 # humo
        if model.fuego[y][x] == 2:
            grid[x][y] = 2                 # fuego
        if model.poi[y][x] == 1 or model.poi[y][x] == 2:
            grid[x][y] = 3                 # marcador boca abajo
        if model.poi[y][x] == 3:
            grid[x][y] = 4                 # victima ya revelada
        if len(content) > 0:
            grid[x][y] = 5                 # el bombero se pinta encima de todo
    return grid


def contar_fuego(model):
    count = 0
    for content, (x, y) in model.grid.coord_iter():
        if model.fuego[y][x] == 2:
            count += 1
    return count  #cuenta las celdas que estan en llamas, sin contar el humo


def contar_rescatando(model):
    count = 0
    for agent in model.agents:
        if agent.papel == "rescate":
            count += 1
    return count  # el datacollector corre antes que los agentes, asi que este es el papel de la ronda pasada


def contar_paredes_danadas(model):
    # una pared de en medio esta escrita en las dos celdas que la comparten, pero
    # una del borde del tablero solo en una, porque afuera no hay celda. por eso
    # las de en medio suman medio y las del borde una entera
    dobles = 0
    solas = 0
    for fila in range(6):
        for col in range(8):
            for direccion in range(4):
                borde = model.paredes[fila][col][direccion]
                if borde == 2 or borde == 3:
                    if celda_vecina(fila, col, direccion) == None:
                        solas += 1
                    else:
                        dobles += 1
    return dobles // 2 + solas


def contar_puertas_abiertas(model):
    count = 0
    for fila in range(6):
        for col in range(8):
            for direccion in range(4):
                borde = model.paredes[fila][col][direccion]
                if borde == 5 or borde == 6:
                    count += 1
    return count // 2   # mismo caso, el borde esta escrito de los dos lados


class FlashPointModel(Model):
    def __init__(self, estrategia="mejorada", avances=1, ganar=7, perder=4,
                 colapso=24, rescatistas=2, ruta="../tableros/tablero_final.txt",
                 **kwargs):
        super().__init__(**kwargs)

        # fuego.py, poi.py y bombero.py sacan sus numeros de np.random, que es el
        # generador global y no es el que siembra batch_run con rng. Si no se
        # siembra aqui, dos corridas con la misma semilla salen distintas
        np.random.seed(int(self.rng.integers(0, 2 ** 31 - 1)))

        self.grid = MultiGrid(8, 6, torus=False)   # 8 de ancho por 6 de alto

        # las cuatro capas salen del archivo del profe, ya en base 0
        (self.paredes, self.fuego, self.poi, self.salidas) = leer_tab(ruta)

        self.rescatados = 0
        self.perdidas = 0
        self.danio = 0
        self.estado = "en_curso"
        self.avances = avances     # veces que avanza el fuego al cerrar cada turno
        self.ganar = ganar
        self.perder = perder
        self.colapso = colapso
        crear_bolsa(self)      # crea model.bolsa por dentro, no devuelve nada

        # los 6 bomberos arrancan repartidos en las 4 salidas, por eso se repiten.
        # unos rescatan y otros apagan, pero el papel solo lo usa el mejorado:
        # el aleatorio lo ignora por completo
        i = 0
        while i < 6:
            if estrategia == "aleatoria":
                agent = Bombero(self)
            else:
                agent = BomberoMejorado(self)
            if i < rescatistas:
                agent.papel = "rescate"
            else:
                agent.papel = "contencion"
            agent.papel_base = agent.papel    # el mejorado necesita saber a cual volver
            (fila, col) = self.salidas[i % len(self.salidas)]
            self.agents.add(agent)
            self.grid.place_agent(agent, (col, fila))
            i += 1

        self.datacollector = DataCollector(
            model_reporters={
                "Grid": get_grid,
                "Rescatados": lambda model: model.rescatados,
                "Perdidas": lambda model: model.perdidas,
                "Danio": lambda model: model.danio,
                "Fuegos": contar_fuego,
                "Paredes": contar_paredes_danadas,
                "Puertas": contar_puertas_abiertas,
                "Rescatando": contar_rescatando,
                "Pasos": lambda model: model.steps,
                "Avances": lambda model: model.avances,
                "Estado": lambda model: model.estado,
            })

    def step(self):
        self.datacollector.collect(self)   # guarda el estado antes de moverlo

        # cada jugador termina su turno avanzando el fuego, asi que no se puede
        # usar shuffle_do: hay que meter el fuego entre un bombero y el siguiente
        bomberos = []
        for agent in self.agents:
            bomberos.append(agent)

        orden = np.random.permutation(len(bomberos))
        for turno in orden:
            bomberos[turno].step()

            i = 0
            while i < self.avances:
                avanzar_fuego(self)
                flashover(self)
                efectos_secundarios(self)
                reponer_poi(self)
                i += 1

            # si la partida se acabo a media ronda los que faltan ya no juegan
            if self.rescatados >= self.ganar:
                break
            if self.perdidas >= self.perder or self.danio >= self.colapso:
                break

        self.revisar_fin()

    def revisar_fin(self):
        if self.rescatados >= self.ganar:
            self.estado = "ganado"
        if self.perdidas >= self.perder:
            self.estado = "perdido"
        if self.danio >= self.colapso:
            self.estado = "perdido"        # el edificio se cae con todos adentro
        if self.estado != "en_curso":
            # el collect del step guarda el estado de ANTES de la ronda, asi que
            # sin esta linea la ronda que gana la partida nunca queda registrada
            self.datacollector.collect(self)
            self.running = False           # asi batch_run corta la corrida sola

    def termino(self):
        return self.estado != "en_curso"


VICTIMAS_PARA_GANAR = 7
VICTIMAS_PARA_PERDER = 4
DANIO_PARA_COLAPSO = 24    # el reglamento son 24 marcadores de dano
AVANCES_POR_BOMBERO = 1    # son 6 bomberos, o sea 6 avances por ronda
RESCATISTAS = 2          # 2 rescatando y 4 conteniendo fue el mejor reparto medido
MAX_PASOS = 200            # freno por si una partida se cicla

if __name__ == "__main__":
    model = FlashPointModel("mejorada", AVANCES_POR_BOMBERO, VICTIMAS_PARA_GANAR,
                            VICTIMAS_PARA_PERDER, DANIO_PARA_COLAPSO, RESCATISTAS)
    i = 0
    while not model.termino() and i < MAX_PASOS:
        model.step()
        i += 1

    print("Termino en", i, "pasos:", model.estado)
    print("Rescatados:", model.rescatados, " Perdidas:", model.perdidas,
          " Danio:", model.danio)
