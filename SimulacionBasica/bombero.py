from mesa import Agent
import numpy as np
from paredes import puede_pasar

#hay muchos cambioFila, cambioCol y opuesto porque necesita revisar las cuatro direcciones, y cada uno define sus listas para que se haga
#igual hay muchos filaVecina, colVecina y borde es porque calculan en donde esta la casilla cercana o vecina, en si calcula fila  y columna vecinal
class Bombero(Agent): 
    def __init__(self, model):
        super().__init__(model)
        self.ap=4 #accion point
        self.guardados=0 
        self.cargando=False
        
    def step(self): 
        self.ap=4+self.guardados #suma puntos mas los puntos guardados
        self.guardados=0
        
        while self.ap>0: 
            col,fila=self.pos
            
            if self.model.fuego[fila][col]==2 and self.ap==1: #comprueba si el fuego esta en un solo punto
                salio=False
                cambioFila=[-1,0,1,0]
                cambioCol=[0,-1,0,1]
                for direccion in range(4):
                    filaVecina=fila+cambioFila[direccion]
                    colVecina=col+cambioCol[direccion]
                    if 0 <=filaVecina <6 and 0<=colVecina<8: 
                        if self.model.fuego[filaVecina][colVecina]!=2: #que no tenga fuego
                            if self.mover(filaVecina, colVecina): #mover el bombeero y checar si se realizo el movimeinto
                                salio=True
                                break
                if not salio: 
                    self.apagar(fila,col)
            else: 
                acciones=self.acciones_posibles()
                if len(acciones)==0:
                    break
                orden=np.random.permutation(len(acciones)) #revuelve el indice de las acciones
                for i in orden:
                    accion, dato1, dato2=acciones[i] 
                    if accion=="mover":  #acciones
                        self.mover(dato1,dato2)
                    elif accion=="apagar":
                        self.apagar(dato1,dato2)
                    elif accion=="puerta":
                        self.abrir_cerrar_puerta(dato1)
                    elif accion=="pared":
                        self.romper_pared(dato1)
                    elif accion=="cargar":
                        self.cargar_victima()
                    elif accion=="dejar":
                        self.dejar_victima()
                    break
        self.guardados=self.ap 
        if self.guardados>4:
            self.guardados=4
    def acciones_posibles(self): 
        acciones=[]
        col,fila=self.pos
        cambioFila=[-1,0,1,0] #busca una casilla segura 
        cambioCol=[0,-1,0,1]
        
        if self.ap>=1 and self.model.fuego[fila][col] !=0:
            acciones.append(("apagar", fila,col)) #opcion de apagar casilla
        for direccion in range(4):
            filaVecina=fila+cambioFila[direccion]
            colVecina=col+cambioCol[direccion]
            if 0<=filaVecina<6 and 0 <=colVecina<8:
                borde=self.model.paredes[fila][col][direccion] 
                if puede_pasar(self.model, fila, col,direccion):
                    costo=1 #calcula el costo del moevimeinto
                    if self.cargando:
                        costo=2
                    fuegoVecino=self.model.fuego[filaVecina][colVecina]
                    permitido=True
                    if fuegoVecino==2:
                        costo=2 #vale 2 cuando se lleva a la victima
                        if self.cargando or self.ap<3:
                            permitido=False
                    if permitido and self.ap>=costo: #movimiento y apagado
                        acciones.append(("mover", filaVecina,colVecina))
                    if self.ap>=1 and fuegoVecino!=0: #agrega apagado si la casilla siguiente tiene humo o fuego
                        acciones.append(("apagar", filaVecina, colVecina))
                        
                if self.ap>=1 and (borde==4 or borde==5): 
                    acciones.append(("puerta",direccion,0)) 
                if self.ap>=2 and (borde==1 or borde==2): 
                    acciones.append(("pared", direccion,0))
        if not self.cargando and self.model.poi[fila][col]==3: #agrega cargar a las acciones posibles
            acciones.append(("cargar",0,0))
        if self.cargando and (fila,col)in self.model.salidas:
            acciones.append(("dejar",0,0)) #agrega la opcion de dejar
        return acciones
    
    def mover(self,fila,col):
        colActual, filaActual=self.pos
        cambioFila=[-1,0,1,0]
        cambioCol=[0,-1,0,1]
        direccion=-1 #obtiene la posicion actual, el -1 significa no encontro una direccion valida
        if not(0<=fila<6 and 0<=col<8): #si destino fuera dde tablero
            return False
        for i in range(4): #revisa las direcciones
            if fila==filaActual+cambioFila[i] and col==colActual+cambioCol[i]:
                direccion=i 
        if direccion==-1: 
            return False
        if not puede_pasar(self.model, filaActual,colActual,direccion): #comprueba paso y puntos, no hay movimeinto si hay obstaculo
            return False
        costo=1
        if self.cargando: 
            costo=2 
        if self.model.fuego[fila][col]==2:
            costo=2
            if self.cargando:
                return False
        if self.ap<costo:
            return False
        self.model.grid.move_agent(self, (col,fila)) #movieminto
        self.ap-=costo #descuento
        self.revelar_poi(fila,col) #muestra marcador de casilla
        return True
    
    def apagar(self, fila,col):
        colActual,filaActual=self.pos
        if not (0<=fila<6 and 0<=col<8):
            return False
        if self.ap<1: 
            return False
        permitido=fila==filaActual and col==colActual #donde puede apagar
        cambioFila=[-1,0,1,0]
        cambioCol=[0,-1,0,1]
        for direccion in range(4):
            if fila==filaActual+cambioFila[direccion] and col==colActual+cambioCol[direccion]:
                if puede_pasar(self.model, filaActual, colActual,direccion):
                    permitido=True
        if not permitido:
            return False
        if self.model.fuego[fila][col]==2: #reducir humo o fuego
            self.model.fuego[fila][col]=1
        elif self.model.fuego[fila][col]==1:
            self.model.fuego[fila][col]=0
        else:
            return False
        self.ap-=1 #baja un nivel, de que fuego a humo o humo a nada
        return True
    
    def abrir_cerrar_puerta(self,direccion):
        if direccion<0 or direccion >3 or self.ap<1:
            return False
        col, fila=self.pos
        cambioFila=[-1,0,1,0]
        cambioCol=[0,-1,0,1]
        opuesto=[2,3,0,1]
        filaVecina=fila+cambioFila[direccion]
        colVecina=col+cambioCol[direccion]
        if not(0<=filaVecina<6 and 0<=colVecina<8):
            return False 
        borde=self.model.paredes[fila][col][direccion]
        if borde==4: #abrir o cerrar puertas
            nuevo=5
        elif borde==5:
            nuevo=4
        else:
            return False 
        self.model.paredes[fila][col][direccion]=nuevo #ambos lados de la puerta
        self.model.paredes[filaVecina][colVecina][opuesto[direccion]]=nuevo 
        self.ap-=1
        return True
    
    def romper_pared(self,direccion):
        if direccion<0 or direccion >3 or self.ap<2: 
            return False
        col, fila=self.pos
        cambioFila=[-1,0,1,0]
        cambioCol=[0,-1,0,1]
        opuesto=[2,3,0,1]
        filaVecina=fila+cambioFila[direccion]
        colVecina=col+cambioCol[direccion]
        borde=self.model.paredes[fila][col][direccion]
        if borde!=1 and borde!=2:
            return False
        self.model.paredes[fila][col][direccion]=borde+1 #golpear una pared
        if 0<=filaVecina<6 and 0<=colVecina<8:
            self.model.paredes[filaVecina][colVecina][opuesto[direccion]]=borde+1 
        self.ap-=2 #cambia de estado intacta a dañaday de dañada a destruida
        self.model.danio+=1
        return True
    
    def revelar_poi(self,fila,col):
        colActual, filaActual=self.pos
        if fila!=filaActual or col!=colActual:
            return False
        if self.model.poi[fila][col]==1: #revela poi, si es 1 es una victima oculta, 3 es que una victima se ha reveado
            self.model.poi[fila][col]=3
        elif self.model.poi[fila][col]==2: #2 alarma falsa, 0 elimna el marcador
            self.model.poi[fila][col]=0
        else:
            return False
        return True 
    
    def cargar_victima(self):
        col,fila=self.pos 
        if not self.cargando and self.model.poi[fila][col]==3: #si no lleva otra victima y hay una cerca, la carga y eso hace que no se represente dos veces
            self.cargando=True
            self.model.poi[fila][col]=0
            return True
        return False 
    
    def dejar_victima(self):
        col,fila=self.pos
        if self.cargando and (fila,col) in self.model.salidas: #si el bombero esta en una salida llevando una victima, suma un rescate y la deja, sino devuelve false
            self.model.rescatados +=1
            self.cargando=False
            return True
        return False
            
