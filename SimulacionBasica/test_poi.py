import types
import numpy as np
from tablero import leer_tab
from poi import crear_bolsa, contar_poi, sacar_de_la_bolsa, reponer_poi

# ============================================================
# NOTA: cambia esta ruta si tu tablero_final.txt real ya esta
# en tableros/ en vez de tableros_test/
# ============================================================
paredes, fuego, poi, salidas = leer_tab("../tableros/tablero_final.txt")

# modelo falso: le agregamos .bomberos como lista vacia por ahora,
# porque agente.py todavia no existe. En cuanto Sergio o David
# tengan bomberos de verdad, cambiar esta lista por bomberos reales
# para probar tambien el caso "hay_bombero" de reponer_poi.
model = types.SimpleNamespace(paredes=paredes, fuego=fuego, poi=poi, bomberos=[])

crear_bolsa(model)
print("Tamano inicial de la bolsa:", len(model.bolsa), "(esperado 8 v + 4 f = 12)")
print("Marcadores en tablero al inicio:", contar_poi(model), "(esperado 3)")
print()

# Simular 20 turnos: en cada uno, "rescatamos" un marcador al azar
# (lo ponemos en 0, como si un bombero lo hubiera sacado) y luego
# llamamos reponer_poi, checando que siempre queden 3 (o menos si
# ya no queda nada en la bolsa).
# OJO: victimas y falsas alarmas se cuentan POR SEPARADO, el limite
# de 10 es solo para victimas, las falsas alarmas son un balde
# aparte de 5.
victimas_retiradas = 0
falsas_retiradas = 0
for turno in range(20):
    # buscar un marcador existente y quitarlo, simulando un rescate
    # (valor 1 o 3 = victima, valor 2 = falsa alarma)
    encontrado = False
    for fila in range(6):
        for col in range(8):
            valor = model.poi[fila][col]
            if valor == 1 or valor == 3:
                model.poi[fila][col] = 0
                victimas_retiradas += 1
                encontrado = True
                break
            elif valor == 2:
                model.poi[fila][col] = 0
                falsas_retiradas += 1
                encontrado = True
                break
        if encontrado:
            break

    reponer_poi(model)
    total_tablero = contar_poi(model)
    print("Turno", turno, "- en tablero:", total_tablero, "- bolsa restante:", len(model.bolsa),
          "- victimas fuera:", victimas_retiradas, "- falsas fuera:", falsas_retiradas)
    if total_tablero > 3:
        print("  ERROR: nunca deberia haber mas de 3")

# el limite real: victimas retiradas + las que sigan en el tablero (1 o 3) nunca pasa de 10
victimas_en_tablero = 0
for fila in range(6):
    for col in range(8):
        if model.poi[fila][col] == 1 or model.poi[fila][col] == 3:
            victimas_en_tablero += 1
total_victimas = victimas_retiradas + victimas_en_tablero
print()
print("Total de victimas (retiradas + en tablero):", total_victimas, "(nunca debe pasar de 10)")