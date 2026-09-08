# Aqui se va a generar los códigos del bombero (clase Agent) con self.state

# Aqui posiblemente podemos tener los roles del bombero si quieren ponerlos?

class Bombero (Agent):
    def __init__ (self, model):
        super().__init__(model)

        # Primero a definir las diferentes variables iniciales del bombero.

        self.state = 0 # Estado entre buscar una POI y si esta cargando una victima
        self.carrying = None # Esta cargando una victima?
        self.ap = 4 # Ap con el que inicia

    # Como va a detectar su entorno y que cambia

    def step(self):
        self.neighborhood = self.get_valid_neighborhoods(self.pos)

        if self.state == 0:
            self.buscar_poi()
        else:
            self.llevar_a_salida()