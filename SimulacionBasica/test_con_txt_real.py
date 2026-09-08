import types
from tablero import leer_tab
from paredes import es_valida, celda_vecina, puede_pasar, vecinos_accesibles

paredes, fuego, poi, salidas = leer_tab("../tableros/tablero_final.txt")
model = types.SimpleNamespace(paredes=paredes)

print("celda (0,0):", paredes[0][0], "(esperado [1. 1. 0. 0.])")
print("vecinos_accesibles(0,0):", vecinos_accesibles(model, 0, 0))
print("  (esperado [(1, 0), (0, 1)] -> solo abajo y derecha)")
print()

encontrada = False
for fila in range(6):
    for col in range(8):
        for direccion in range(4):
            if paredes[fila][col][direccion] == 4:
                print("Puerta cerrada en fila", fila, "col", col, "direccion", direccion)
                print("  puede_pasar ahi:", puede_pasar(model, fila, col, direccion), "(esperado False)")
                encontrada = True
                break
        if encontrada:
            break
    if encontrada:
        break

for fila in range(6):
    for col in range(8):
        vecinos = vecinos_accesibles(model, fila, col)
        if len(vecinos) == 4:
            print()
            print("Celda totalmente abierta en fila", fila, "col", col)
            print("  vecinos_accesibles:", vecinos)
            break