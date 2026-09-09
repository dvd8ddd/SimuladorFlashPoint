# Cliente de prueba: hace lo mismo que va a hacer Unity, pero desde python.
# Sirve para comprobar que el servidor manda bien el JSON sin tener que abrir
# el editor. Se corre con el servidor ya levantado en otra terminal:
#   terminal 1:  python server.py 8585
#   terminal 2:  python prueba_cliente.py
import urllib.request
import json

DIRECCION = "http://localhost:8585"


def pedir(metodo):
    if metodo == "GET":
        peticion = urllib.request.Request(DIRECCION)
    else:
        peticion = urllib.request.Request(DIRECCION, data=b"")
    respuesta = urllib.request.urlopen(peticion)
    texto = respuesta.read().decode("utf-8")
    return json.loads(texto)


def revisar_forma(estado):
    # los mismos campos y largos que dice el contrato, porque si algo no cuadra
    # JsonUtility de Unity no marca error, nada mas deja los campos en cero
    problemas = []
    campos = ["paso", "estado", "bomberos", "fuego", "poi", "paredes",
              "rescatados", "perdidas", "danio"]
    for campo in campos:
        if campo not in estado:
            problemas.append("falta el campo " + campo)

    if len(estado["fuego"]) != 48:
        problemas.append("fuego tiene " + str(len(estado["fuego"])) + " y deben ser 48")
    if len(estado["poi"]) != 48:
        problemas.append("poi tiene " + str(len(estado["poi"])) + " y deben ser 48")
    if len(estado["paredes"]) != 192:
        problemas.append("paredes tiene " + str(len(estado["paredes"])) + " y deben ser 192")
    if len(estado["bomberos"]) != 6:
        problemas.append("hay " + str(len(estado["bomberos"])) + " bomberos y deben ser 6")

    for bombero in estado["bomberos"]:
        if not (0 <= bombero["fila"] < 6):
            problemas.append("bombero " + str(bombero["id"]) + " fuera del tablero")
        if not (0 <= bombero["col"] < 8):
            problemas.append("bombero " + str(bombero["id"]) + " fuera del tablero")

    return problemas


def pintar(estado):
    # dibuja el tablero como lo va a dibujar Unity, indexando la lista aplanada
    # con fila * 8 + col
    ocupadas = []
    for bombero in estado["bomberos"]:
        ocupadas.append((bombero["fila"], bombero["col"]))

    for fila in range(6):
        renglon = ""
        for col in range(8):
            i = fila * 8 + col
            simbolo = "."
            if estado["fuego"][i] == 1:
                simbolo = "h"                  # humo
            if estado["fuego"][i] == 2:
                simbolo = "F"                  # fuego
            if estado["poi"][i] == 1 or estado["poi"][i] == 2:
                simbolo = "?"                  # marcador boca abajo
            if estado["poi"][i] == 3:
                simbolo = "V"                  # victima revelada
            if (fila, col) in ocupadas:
                simbolo = "B"                  # bombero
            renglon += simbolo + " "
        print("   " + renglon)


estado = pedir("GET")          # el GET reinicia la partida
print("Partida nueva. Tablero inicial:")
pintar(estado)

problemas = revisar_forma(estado)
if len(problemas) == 0:
    print("\nEl JSON trae la forma del contrato: 48 fuego, 48 poi, 192 paredes, 6 bomberos.")
else:
    for problema in problemas:
        print("PROBLEMA:", problema)

print("\nCorriendo la partida...")
ronda = 0
while estado["estado"] == "en_curso" and ronda < 200:
    estado = pedir("POST")
    ronda += 1
    problemas = revisar_forma(estado)
    if len(problemas) > 0:
        for problema in problemas:
            print("PROBLEMA en la ronda", ronda, ":", problema)
        break

print("Ronda", estado["paso"], "->", estado["estado"],
      "| rescatados", estado["rescatados"],
      "| perdidas", estado["perdidas"],
      "| danio", estado["danio"])
print("\nTablero final:")
pintar(estado)
print("\nSe hicieron", ronda, "peticiones POST y todas contestaron bien.")
