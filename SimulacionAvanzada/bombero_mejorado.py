# Estrategia mejorada: roles fijos y rutas con dijkstra.
# Hereda del Bombero de la simulacion aleatoria y solo cambia el step(), o sea
# solo cambia como decide. Las acciones (mover, apagar, cargar, dejar) son las
# mismas y con las mismas reglas del juego.
from bombero import Bombero
from paredes import puede_pasar, celda_vecina
from pathfinding import dijkstra, costos, INFINITE


class BomberoMejorado(Bombero):
    def __init__(self, model):
        super().__init__(model)
        self.papel = "rescate"     # el modelo lo cambia a "contencion" a la mitad
        self.objetivo = None       # a que celda va, para no ir todos a la misma

    def step(self):
        self.ap = 4 + self.guardados
        self.guardados = 0

        while self.ap > 0:
            if self.actuar_aqui():
                continue           # hizo algo en su celda, vuelve a revisar
            if not self.avanzar():
                break              # ya no alcanza el ap o no hay a donde ir

        self.guardados = self.ap
        if self.guardados > 4:
            self.guardados = 4

    # ------------------------------------------------------------------
    # lo que puede hacer sin moverse
    # ------------------------------------------------------------------
    def actuar_aqui(self):
        (col, fila) = self.pos

        if self.cargando and (fila, col) in self.model.salidas:
            if self.dejar_victima():
                self.objetivo = None
                return True

        if self.papel == "rescate" and not self.cargando:
            if self.model.poi[fila][col] == 3:
                if self.cargar_victima():
                    self.objetivo = None
                    return True

        if self.toca_apagar() and self.ap >= 1:
            # primero las llamas, que son las que explotan y danan el edificio
            if self.model.fuego[fila][col] == 2:
                self.apagar(fila, col)
                self.objetivo = None
                return True
            for direccion in range(4):
                if not puede_pasar(self.model, fila, col, direccion):
                    continue
                vecina = celda_vecina(fila, col, direccion)
                if self.model.fuego[vecina[0]][vecina[1]] == 2:
                    self.apagar(vecina[0], vecina[1])
                    self.objetivo = None
                    return True
            # ya sin llamas alrededor, el humo tambien se limpia: si se queda
            # ahi el flashover lo vuelve a prender y el ap gastado se pierde
            if self.model.fuego[fila][col] == 1:
                self.apagar(fila, col)
                self.objetivo = None
                return True
            for direccion in range(4):
                if not puede_pasar(self.model, fila, col, direccion):
                    continue
                vecina = celda_vecina(fila, col, direccion)
                if self.model.fuego[vecina[0]][vecina[1]] == 1:
                    self.apagar(vecina[0], vecina[1])
                    self.objetivo = None
                    return True

        return False

    def toca_apagar(self):
        if self.papel == "contencion":
            return True
        if self.cargando:
            return False
        # rescatista sin nadie a quien ir a buscar: mientras tanto apaga
        for fila in range(6):
            for col in range(8):
                if self.model.poi[fila][col] > 0:
                    return False
        return True

    # ------------------------------------------------------------------
    # a donde va y como se mueve
    # ------------------------------------------------------------------
    def avanzar(self):
        (col, fila) = self.pos
        destino = self.buscar_destino()
        if destino is None:
            return False

        self.objetivo = destino
        matrix = costos(self.model, self.cargando)
        (distancia, camino) = dijkstra(self.model, matrix, (fila, col), destino)
        if len(camino) < 2:
            return False           # no hay ruta hasta alla

        siguiente = camino[1]
        return self.mover(siguiente[0], siguiente[1])

    def buscar_destino(self):
        if self.cargando:
            return self.mas_cercana(self.model.salidas)

        if self.toca_apagar():
            candidatas = []
            for fila in range(6):
                for col in range(8):
                    if self.model.fuego[fila][col] == 2:
                        candidatas.append((fila, col))
            if len(candidatas) == 0:
                return None
            return self.mas_cercana(candidatas)

        candidatas = []
        revelados = []
        for fila in range(6):
            for col in range(8):
                if self.model.poi[fila][col] > 0:
                    candidatas.append((fila, col))
                if self.model.poi[fila][col] == 3:
                    revelados.append((fila, col))

        # una victima ya destapada vale mas que un marcador que puede ser falso
        if len(revelados) > 0:
            candidatas = revelados

        # los rescatistas no se pelean el mismo marcador
        libres = []
        for celda in candidatas:
            if not self.esta_tomada(celda):
                libres.append(celda)
        if len(libres) > 0:
            candidatas = libres

        if len(candidatas) == 0:
            return None
        return self.mas_cercana(candidatas)

    def mas_cercana(self, celdas):
        (col, fila) = self.pos
        matrix = costos(self.model, self.cargando)
        mejor = None
        mejor_dist = INFINITE
        for celda in celdas:
            if celda == (fila, col):
                continue
            (distancia, camino) = dijkstra(self.model, matrix, (fila, col), celda)
            if distancia < mejor_dist:
                mejor_dist = distancia
                mejor = celda
        return mejor

    def esta_tomada(self, celda):
        for otro in self.model.agents:
            if otro is self:
                continue
            if otro.objetivo == celda:
                return True
        return False
