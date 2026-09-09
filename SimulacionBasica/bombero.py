from mesa import Agent
import numpy as np
from paredes import puede_pasar

class Bombero(Agent):
    def __init__(self, model):
        super().__init__(model)
        self.ap=4
        self.guardados=0
        self.cargando=False
        
    def step(self):
        self.ap=4+self.guardados
        self.guardados=0
        
        while self.ap>0:
            col,fila=self.pos
            
            if self.model.fuego[fila][col]==2 and self.ap==1:
                salio=False
                cambioFila=[-1,0,1,0]
                cambioCol=[0,-1,0,1]
                for direccion in range(4):
                    filaVecina=fila+cambioFila[direccion]
                    colVecina=col+cambioCol[direccion]
                    if 0 <=filaVecina <6 and 0<=colVecina<8:
                        if self.model.fuego[filaVecina][colVecina]!=2:
                            if self.mover(filaVecina, colVecina):
                                salio=True
                                break
                if not salio:
                    self.apagar(fila,col)
            else:
                acciones=self.acciones_posibles()
                if len(acciones)==0:
                    break
                orden=np.random.permutation(len(acciones))
                for i in orden:
                    accion, dato1, dato2=acciones[i] 
                    if accion=="mover":
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
        cambioFila=[-1,0,1,0]
        cambioCol=[0,-1,0,1]
        
        if self.ap>=1 and self.model.fuego[fila][col] !=0:
            acciones.append(("apagar", fila,col))
        for direccion in range(4):
            filaVecina=fila+cambioFila[direccion]
            colVecina=col+cambioCol[direccion]
            if 0<=filaVecina<6 and 0 <=colVecina<8:
                borde=self.model.paredes[fila][col][direccion]
                if puede_pasar(self.model, fila, col,direccion):
                    costo=1
                    if self.cargando:
                        costo=2
                    fuegoVecino=self.model.fuego[filaVecina][colVecina]
                    permitido=True
                    if fuegoVecino==2:
                        costo=2
                        if self.cargando or self.ap<3:
                            permitido=False
                    if permitido and self.ap>=costo:
                        acciones.append(("mover", filaVecina,colVecina))
                    if self.ap>=1 and fuegoVecino!=0:
                        acciones.append(("apagar", filaVecina, colVecina))
                        
                if self.ap>=1 and (borde==4 or borde==5):
                    acciones.append(("puerta",direccion,0)) 
                if self.ap>=2 and (borde==1 or borde==2):
                    acciones.append(("pared", direccion,0))
        if not self.cargando and self.model.poi[fila][col]==3:
            acciones.append(("cargar",0,0))
        if self.cargando and (fila,col)in self.model.salidas:
            acciones.append(("dejar",0,0))
        return acciones
    
    def mover(self,fila,col):
        colActual, filaActual=self.pos
        cambioFila=[-1,0,1,0]
        cambioCol=[0,-1,0,1]
        direccion=-1
        if not(0<=fila<6 and 0<=col<8):
            return False
        for i in range(4):
            if fila==filaActual+cambioFila[i] and col==colActual+cambioCol[i]:
                direccion=i 
        if direccion==-1:
            return False
        if not puede_pasar(self.model, filaActual,colActual,direccion):
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
        self.model.grid.move_agent(self, (col,fila))
        self.ap-=costo 
        self.revelar_poi(fila,col)
        return True
    
    def apagar(self, fila,col):
        colActual,filaActual=self.pos
        if not (0<=fila<6 and 0<=col<8):
            return False
        if self.ap<1: 
            return False
        permitido=fila==filaActual and col==colActual
        cambioFila=[-1,0,1,0]
        cambioCol=[0,-1,0,1]
        for direccion in range(4):
            if fila==filaActual+cambioFila[direccion] and col==colActual+cambioCol[direccion]:
                if puede_pasar(self.model, filaActual, colActual,direccion):
                    permitido=True
        if not permitido:
            return False
        
        if self.model.fuego[fila][col]==2:
            self.model.fuego[fila][col]=1
        elif self.model.fuego[fila][col]==1:
            self.model.fuego[fila][col]=0
        else:
            return False
        self.ap-=1 
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
        if borde==4:
            nuevo=5
        elif borde==5:
            nuevo=4
        else:
            return False 
        self.model.paredes[fila][col][direccion]=nuevo
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
        self.model.paredes[fila][col][direccion]=borde+1
        if 0<=filaVecina<6 and 0<=colVecina<8:
            self.model.paredes[filaVecina][colVecina][opuesto[direccion]]=borde+1 
        self.ap-=2
        self.model.danio+=1
        return True
    
    def revelar_poi(self,fila,col):
        colActual, filaActual=self.pos
        if fila!=filaActual or col!=colActual:
            return False
        if self.model.poi[fila][col]==1:
            self.model.poi[fila][col]=3
        elif self.model.poi[fila][col]==2:
            self.model.poi[fila][col]=0
        else:
            return False
        return True 
    
    def cargar_victima(self):
        col,fila=self.pos 
        if not self.cargando and self.model.poi[fila][col]==3:
            self.cargando=True
            self.model.poi[fila][col]=0
            return True
        return False 
    
    def dejar_victima(self):
        col,fila=self.pos
        if self.cargando and (fila,col) in self.model.salidas:
            self.model.rescatados +=1
            self.cargando=False
            return True
        return False
            
