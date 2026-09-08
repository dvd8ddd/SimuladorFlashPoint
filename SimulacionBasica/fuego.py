import numpy as np

def avanzar_fuego(model):
    fila=np.random.randint(6) #eesta y abajo escogen la casilla, elige una fila de 0 a 5 y columna de 0 a 7
    col=np.random.randint(8)
    if model.fuego[fila][col]==0: #aqui se pone el humo
        model.fuego[fila][col]=1
        cambioFila=[-1,0,1,0] #esta y abajo son direcciones
        cambioCol=[0,-1,0,1]
        
        for direccion in range(4): #revia los vecinos del humo
            filaVecina= fila+cambioFila[direccion]
            colVecina=col+cambioCol[direccion]
            
            if 0<=filaVecina <6 and 0<= colVecina<8:#calcula la posucion
                borde=model.paredes[fila][col][direccion]
                if borde==0 or borde==3 or borde==5 or borde==6:
                    if model.fuego[filaVecina][colVecina]==2:
                        model.fuego[fila][col]=2
    
    elif model.fuego[fila][col]==1: #resuelve el humo o fuego que existia
        model.fuego[fila][col]=2
    elif model.fuego[fila][col]==2:
        explosion(model, fila, col)
        
def explosion(model,fila,col):
    cambioFila=[-1,0,1,0]
    cambioCol=[0,-1,0,1]
    opuesto=[2,3,0,1] #explosion
    
    for direccion in range(4):
        filaActual=fila
        colActual=col
        continuar=True
        
        while continuar: #revisa el proximo paso de la onda
            filaVecina=filaActual+cambioFila[direccion]
            colVecina=colActual+cambioCol[direccion]
            dentro=0<=filaVecina<6 and 0<=colVecina<8
            borde=model.paredes[filaActual][colActual][direccion]
            opuesta=opuesto[direccion]
    
            if borde==1 or borde==2: #golpea pared
                model.paredes[filaActual][colActual][direccion]=borde+1
                if dentro:
                    model.paredes[filaVecina][colVecina][opuesta]=borde+1
                model.danio+=1
                continuar=False
            
            elif borde==4: #golpea puerta cerrada
                model.paredes[filaActual][colActual][direccion]=6
                if dentro:
                    model.paredes[filaVecina][colVecina][opuesta]=6
                continuar=False
                
            elif borde==0 or borde==3 or borde==5  or borde==6: #avanza por borde que se puede pasar
                if dentro:
                    if model.fuego[filaVecina][colVecina]==2:
                        filaActual=filaVecina
                        colActual=colVecina
                    else:
                        model.fuego[filaVecina][colVecina]=2
                        continuar=False
                else:
                    continuar=False
                
def flashover(model):
    cambioFila=[-1,0,1,0]
    cambioCol=[0,-1,0,1]
    cambio=True
    
    while cambio: #perimite el primer recorrido y reinicia el aviso de cambios al comenzar cada recorrido
        cambio=False 
        for fila in range(6): #busca humo para prender
            for col in range(8):
                if model.fuego[fila][col]==1:
                    for direccion in range(4):
                        filaVecina=fila+cambioFila[direccion]
                        colVecina=col+cambioCol[direccion]
                        
                        if 0<=filaVecina<6 and 0<=colVecina<8:
                            borde=model.paredes[fila][col][direccion]
                            if borde==0 or borde==3 or borde==5 or borde==6:
                                if model.fuego[filaVecina][colVecina]==2:
                                    model.fuego[fila][col]=2
                                    cambio=True
def efectos_secundarios(model):
    for bombero in model.agents: #revisa bombero
        col,fila=bombero.pos
        if model.fuego[fila][col]==2:
            filaSalida, colSalida=model.salidas[0] #guarda primera salida
        pocaDistancia=abs(fila-filaSalida)+abs(col-colSalida) 
        for salida in model.salidas: #compara las diferentes salidas
            filaOpcional, colOpcional=salida
            distancia=abs(fila-filaOpcional)+abs(col-colOpcional) 
            
            if distancia<pocaDistancia:
                pocaDistancia=distancia
                filaSalida=filaOpcional
                colSalida=colOpcional
        if bombero.cargando: #aqui es perder la victima mienrtras el bombero la carga
            model.perdidas+=1
            bombero.cargando=False
        model.grid.move_agent(bombero, (colSalida,filaSalida))

    for fila in range(6): #eliminar poi quemadso
        for col in range(8):
            if model.fuego[fila][col]==2:
                if model.poi[fila][col]==1 or model.poi[fila][col]==3: #recorre tablero buscando poi en casillas con fuego
                    model.perdidas+=1
                    model.poi[fila][col]=0
                elif model.poi[fila][col]==2:
                    model.poi[fila][col]=0
            
