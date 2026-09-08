

def crear_bolsa(model):
    # 10 victimas y 5 falsas alarmas en total, menos las 3 que ya
    # vienen puestas en el tablero menos las que ya estan puestas por def:
    # 8 victimas y 4 falsas alarmas
    victimas_en_tablero = 0
    falsas_en_tablero = 0
    for fila in range(6):
        for col in range(8):
            valor = model.poi[fila][col]
            if valor == 1 or valor == 3:
                victimas_en_tablero += 1
            elif valor == 2:
                falsas_en_tablero += 1
    victimas_restantes = 10 - victimas_en_tablero
    falsas_restantes = 5 - falsas_en_tablero
    bolsa = []
    for i in range(victimas_restantes):
        bolsa.append("v")
    for i in range(falsas_restantes):
        bolsa.append("f")
    model.bolsa = bolsa

def contar_poi(model):
    # cuenta cuantas casillas valen 1, 2 o 3 (boca abajo + reveladas)

    total = 0
    for fila in range(6):
        for col in range(8):
            valor = model.poi[fila][col]
            if valor == 1 or valor == 2 or valor == 3:
                total += 1
    return total

def sacar_de_la_bolsa(model):
    # saca uno al azar de lo que quede, lo quita de la bolsa,
    # regresa 1 (victima) o 2 (falsa alarma)

    indice = int(np.random.randint(len(model.bolsa)))
    tipo = model.bolsa[indice]
    del model.bolsa[indice]
    if tipo == "v":
        return 1
    else:
        return 2

def reponer_poi(model):
    # mientras haya menos de 3 en el tablero y quede algo en la bolsa:
    #   escoge casilla al azar, si tiene fuego/humo lo quita antes,
    #   si tiene bombero se revela de inmediato (1->3, 2 se quita),
    #   si ya tiene marcador, escoge otra casilla

    while contar_poi(model) < 3:
        if len(model.bolsa) == 0:
            break
 
        fila = int(np.random.randint(6))
        col = int(np.random.randint(8))
 
        if model.poi[fila][col] != 0:
            continue
 
        if model.fuego[fila][col] != 0:
            model.fuego[fila][col] = 0
 
        hay_bombero = False
        for bombero in model.bomberos:
            if bombero.fila == fila and bombero.col == col:
                hay_bombero = True
                break
 
        valor = sacar_de_la_bolsa(model)
 
        if hay_bombero:
            if valor == 1:
                model.poi[fila][col] = 3
            # si valor es 2 (falsa alarma) no se coloca nada, ya se descarto
        else:
            model.poi[fila][col] = valor