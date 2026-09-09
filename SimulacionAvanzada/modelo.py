# Requiero Mesa > 3.3
# Modelo de Flash Point Fire Rescue, reglas del Family Game Setup.
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

import numpy as np

# archivos del equipo. ninguno de ellos importa a este, para no hacer un circulo
from tablero import leer_tab
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


class FlashPointModel(Model):
    def __init__(self, estrategia="mejorada", avances=6, ganar=7, perder=4,
                 colapso=24, rescatistas=3, ruta="../tableros/tablero_final.txt",
                 **kwargs):
        super().__init__(**kwargs)
        self.grid = MultiGrid(8, 6, torus=False)   # 8 de ancho por 6 de alto

        # las cuatro capas salen del archivo del profe, ya en base 0
        (self.paredes, self.fuego, self.poi, self.salidas) = leer_tab(ruta)

        self.rescatados = 0
        self.perdidas = 0
        self.danio = 0
        self.estado = "en_curso"
        self.avances = avances     # cuantas veces avanza el fuego por ronda
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
                "Pasos": lambda model: model.steps,
                "Avances": lambda model: model.avances,
                "Estado": lambda model: model.estado,
            })

    def step(self):
        self.datacollector.collect(self)   # guarda el estado antes de moverlo

        self.agents.shuffle_do("step")     # los 6 bomberos toman su turno

        # en el juego de mesa cada jugador termina su turno avanzando el fuego,
        # asi que una ronda de 6 bomberos son 6 avances
        i = 0
        while i < self.avances:
            avanzar_fuego(self)
            flashover(self)
            efectos_secundarios(self)
            reponer_poi(self)
            i += 1

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
AVANCES_POR_RONDA = 6
RESCATISTAS = 3
MAX_PASOS = 200            # freno por si una partida se cicla

if __name__ == "__main__":
    model = FlashPointModel("mejorada", AVANCES_POR_RONDA, VICTIMAS_PARA_GANAR,
                            VICTIMAS_PARA_PERDER, DANIO_PARA_COLAPSO, RESCATISTAS)
    i = 0
    while not model.termino() and i < MAX_PASOS:
        model.step()
        i += 1

    print("Termino en", i, "pasos:", model.estado)
    print("Rescatados:", model.rescatados, " Perdidas:", model.perdidas, " Danio:", model.danio)
