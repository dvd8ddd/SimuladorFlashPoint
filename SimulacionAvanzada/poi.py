import numpy as np

# ============================================================
# NOTAS PARA HABLAR CON EL EQUIPO (borrar cuando ya se resuelvan)
#
# 1. model.bomberos -> en reponer_poi() se asume que existe una
#    lista model.bomberos, donde cada bombero tiene .fila y .col
#    (mismo patron que paredes.py). Esto todavia no existe en
#    ningun otro archivo porque agente.py de David no esta listo.
#    HABLAR CON SERGIO: confirmar que su modelo.py va a exponer
#    model.bomberos con esa forma exacta, o avisar si va a ser
#    distinto (ej. una lista de tuplas, un dict, etc.) para
#    ajustar el for de abajo.
#
# 2. model.bolsa -> esta funcion crea el atributo model.bolsa la
#    primera vez que se llama crear_bolsa(model). Falta acordar
#    CUANDO se llama exactamente (una sola vez al preparar la
#    partida, dentro de __init__ de FlashPointModel, antes del
#    primer step()). Si nadie la llama antes de reponer_poi(),
#    va a tronar con AttributeError: 'model' no tiene .bolsa.
#
# 3. model.fuego y model.poi -> se asume que ya vienen como
#    matrices 6x8 de numpy, resultado de tablero.leer_tab(). Si
#    en algun momento el tipo de dato cambia (por ejemplo si se
#    convierten a listas normales de Python en vez de np.array),
#    esta funcion deberia seguir funcionando igual porque solo
#    usa indexado [fila][col], pero vale la pena confirmarlo.
# ============================================================


def crear_bolsa(model):
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
    total = 0
    for fila in range(6):
        for col in range(8):
            valor = model.poi[fila][col]
            if valor == 1 or valor == 2 or valor == 3:
                total += 1
    return total


def sacar_de_la_bolsa(model):
    # np.random, no random -> asi lo pide el brief, igual que
    # el resto de los archivos del profe
    indice = int(np.random.randint(len(model.bolsa)))
    tipo = model.bolsa[indice]
    del model.bolsa[indice]
    if tipo == "v":
        return 1
    else:
        return 2


def reponer_poi(model):
    while contar_poi(model) < 3:
        if len(model.bolsa) == 0:
            break

        fila = int(np.random.randint(6))
        col = int(np.random.randint(8))

        if model.poi[fila][col] != 0:
            continue

        if model.fuego[fila][col] != 0:
            model.fuego[fila][col] = 0

        # RESPUESTA A LA NOTA 1: no hay model.bomberos. Los agentes viven en
        # model.agents (asi los guarda Mesa 3) y su posicion es agent.pos, que
        # viene como (columna, fila) porque el grid de Mesa va al reves que
        # nuestras capas
        hay_bombero = False
        for bombero in model.agents:
            (col_bombero, fila_bombero) = bombero.pos
            if fila_bombero == fila and col_bombero == col:
                hay_bombero = True
                break

        valor = sacar_de_la_bolsa(model)

        if hay_bombero:
            if valor == 1:
                model.poi[fila][col] = 3
            # si valor es 2 (falsa alarma) no se coloca nada,
            # se descarta de inmediato sin pasar por el tablero
        else:
            model.poi[fila][col] = valor