import numpy as np

def leer_tab(ruta):
    archivo=open(ruta, "r")
    lineas=archivo.readlines()
    archivo.close()

    #matriz de paredes 6x8, c/celda guarda arriba, abajo, ziqueirda y derecha
    paredes=np.zeros((6,8,4))
    fuego=np.zeros((6,8))
    poi=np.zeros((6,8))
    salidas=[]
    indice=0

    #6x8, los 8 tienen 4 digitos
    for fila in range(6):
        linea=lineas[indice].split()
        for col in range(8):
            codigo = linea[col]
            paredes[fila][col][0]=int(codigo[0])
            paredes[fila][col][1]=int(codigo[1])
            paredes[fila][col][2]=int(codigo[2])
            paredes[fila][col][3]=int(codigo[3])
        indice +=1 

    #3 lineas de poi
    for i in range(3):
        linea=lineas[indice].split()
        fila=int(linea[0])-1 #separa en strings
        col=int(linea[1])-1
        tipo=linea[2]

        if tipo=="v": #guarda el valor e indica eltipo o de poi
            poi[fila][col]=1
        else:
            poi[fila][col]=2
        indice +=1

    #10 lineas casillas con fuego
    for i in range(10): 
        linea=lineas[indice].split()
        fila=int(linea[0])-1 
        col=int(linea[1])-1
        fuego[fila][col] =2
        indice +=1 #marca

    #8 lineas fila y col
    for i in range(8):
        linea=lineas[indice].split()
        fila1=int(linea[0])-1
        col1=int(linea[1])-1
        fila2=int(linea[2])-1
        col2=int(linea[3])-1

        if fila2==fila1-1:
            paredes[fila1][col1][0]=4 #arriba
            paredes[fila2][col2][2]=4
        elif fila2==fila1+1:
            paredes[fila1][col1][2]=4 #abajo
            paredes[fila2][col2][0]=4
        elif col2==col1-1:
            paredes[fila1][col1][1]=4 #izquierda
            paredes[fila2][col2][3]=4
        elif col2==col1+1:
            paredes[fila1][col1][3]=4 #derecha
            paredes[fila2][col2][1]=4
        indice+=1 #marca
    #4 lineas
    for i in range(4):
        linea=lineas[indice].split()
        fila=int(linea[0])-1
        col=int(linea[1])-1
        salidas.append((fila, col))
        indice +=1
    return paredes, fuego,poi,salidas

paredes, fuego, poi, salidas=leer_tab("tablero/tablero_final.txt") #resultado devuelto
#verificacion
contador_fuego=0
for fila in range(6):
    for col in range(8):
        if fuego[fila][col] == 2:
            contador_fuego += 1
            
contador_poi=0
for fila in range(6):
    for col in range(8):
        if poi[fila][col] !=0:
            contador_poi+=1

contador_puertas=0
for fila in range(6):
    for col in range(8):
        for lado in range(4):
            if paredes[fila][col][lado]==4:
                contador_puertas+=1

print("casillas con fuego:", contador_fuego, "(debe ser 10)")
print("casillas con marcador:", contador_poi, "(debe ser 3)")
print("bordes con puertas:", contador_puertas, "(debe ser 16)")
print("casilla (0,0):", paredes[0][0], "(debe ser [1,1,0,0])")
print("salidas:", salidas, "(debe ser [(0,2), (0,7), (4,0), (5,2)])")
