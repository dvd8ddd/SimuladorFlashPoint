# Cómo se hacen las paredes en el grid sin que pongamos casillas extras?

# Las representamos con números

# 0 = arriba
# 1 = izquierda
# 2 = abajo
# 3 = derecha

# Entonces dentro del model definimos que cada casilla tiene 4 lados
# Pasa de que por ejemplo (x,y) tiene [0, 0, 0, 0] disponibles
# Representando los lados [arriba, izq, abajo, derecha]
# 0 = no pared
# 1 = pared




# La casilla existe? 
# Definir si la coordenada es valida 
# Cómo es 6x8 pasa a 5x7 en código
def es_valida(fila, col):
    if fila < 0 or fila > 5:
        return False
    if col < 0 or col > 7:
        return False
    return True


# Cuales casillas vecinas están en la dirección de un punto?
# Checa las casillas vecinas y luego usa es_valida para calcular
# si esas casillas representan el tablero.
def celda_vecina(fila, col, direccion):
    if direccion == 0: # Arriba = resta 1 a la fila
        fila_v = fila - 1
        col_v = col
    elif direccion == 1: # izquierda = resta 1 a la columna
        fila_v = fila
        col_v = col - 1
    elif direccion == 2: # abajo = suma 1 a la fila
        fila_v = fila + 1
        col_v = col
    elif direccion == 3: # derecha = suma 1 a la columna
        fila_v = fila
        col_v = col + 1
    if es_valida(fila_v, col_v) == False:
        return None
    return (fila_v, col_v)

# Pregunta si puede pasar a esa posicion

# Tiene que ver con los estados que definimos de una pared/puerta

# Nada = 0 | Pasa
# Pared = 1 y 2 (normal y dañada) | No pasa   | 3 (destruida) | Pasa
# Puerta = 4 | No pasa  | 5 (abierta) y 6 (destruida) | Pasa


def puede_pasar(model, fila, col, direccion):
    vecina = celda_vecina(fila, col, direccion)
    if vecina == None:
        return False
    valor = model.paredes[fila][col][direccion]
    if valor == 0 or valor == 3 or valor == 5 or valor == 6:
        return True
    return False



# Se vuelve a llamar a puede_pasar
# Para que regrese las direcciones alrededor del agente que puede utilizar
# para moverse


def vecinos_accesibles(model, fila, col):
    result = []
    if puede_pasar(model, fila, col, 0):
        result.append(celda_vecina(fila, col, 0))
    if puede_pasar(model, fila, col, 1):
        result.append(celda_vecina(fila, col, 1))
    if puede_pasar(model, fila, col, 2):
        result.append(celda_vecina(fila, col, 2))
    if puede_pasar(model, fila, col, 3):
        result.append(celda_vecina(fila, col, 3))
    return result


# El oredn final es

# vecinos_accesibles > puede_pasar > celda_vecina > es_valid

# La una usa la otra que usa la siguiente