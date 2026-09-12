def es_valida(fila, col):
    if fila < 0 or fila > 5:
        return False
    if col < 0 or col > 7:
        return False
    return True



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


def puede_pasar(model, fila, col, direccion):
    vecina = celda_vecina(fila, col, direccion)
    if vecina == None:
        return False
    valor = model.paredes[fila][col][direccion]
    if valor == 0 or valor == 3 or valor == 5 or valor == 6:
        return True
    return False



# Se vuelve a llamar a puede_pasar para que regrese las direcciones  del agente que puede usar para moverse

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
