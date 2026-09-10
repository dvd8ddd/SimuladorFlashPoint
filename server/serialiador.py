# Convierte el estado del modelo al JSON que espera Unity.
# Las tres capas van APLANADAS: JsonUtility de Unity no sabe leer arreglos de
# arreglos, recibe puros ceros y no marca ningun error. El aplanado usa el
# mismo fila * 8 + col del to_int del notebook del profe.
import json


def aplanar(matriz):
    lista = []
    for fila in range(6):
        for col in range(8):
            lista.append(int(matriz[fila][col]))
    return lista


def aplanar_paredes(matriz):
    lista = []
    for fila in range(6):
        for col in range(8):
            for direccion in range(4):
                lista.append(int(matriz[fila][col][direccion]))
    return lista


def estado_json(model):
    # se ordenan por unique_id para que Unity vea siempre el mismo id 0 al 5,
    # porque shuffle_do cambia el orden en que se recorren los agentes
    lista = []
    for agent in model.agents:
        lista.append(agent)
    lista.sort(key=lambda agent: agent.unique_id)

    bomberos = []
    identificador = 0
    for agent in lista:
        (col, fila) = agent.pos
        bomberos.append({
            "id": identificador,
            "fila": int(fila),
            "col": int(col),
            "cargando": agent.cargando,
            "ap": int(agent.ap),
        })
        identificador += 1

    estado = {
        "paso": int(model.steps),
        "estado": model.estado,
        "bomberos": bomberos,
        "fuego": aplanar(model.fuego),
        "poi": aplanar(model.poi),
        "paredes": aplanar_paredes(model.paredes),
        "rescatados": int(model.rescatados),
        "perdidas": int(model.perdidas),
        "danio": int(model.danio),
    }
    return json.dumps(estado)