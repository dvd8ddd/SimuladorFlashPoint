# Corre todas las simulaciones con batch_run y guarda el csv crudo.
# Se corre asi:  python correr_simulaciones.py
from mesa.batchrunner import batch_run
import numpy as np
import pandas as pd
import os
import sys

carpeta = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(carpeta, "..", "SimulacionAvanzada"))

from modelo import FlashPointModel

MAX_PASOS = 200
CORRIDAS = 30
TABLERO = os.path.join(carpeta, "..", "tableros", "tablero_final.txt")

params = {
    "estrategia": ["aleatoria", "mejorada"],
    "avances": [2, 4, 6],
    "rescatistas": [2, 3, 4],
    "ruta": TABLERO,
}

rng = np.random.default_rng(42)
rng_values = rng.integers(0, sys.maxsize, size=(CORRIDAS,))

results = batch_run(
    FlashPointModel,
    parameters=params,
    rng=rng_values.tolist(),
    max_steps=MAX_PASOS,
    number_processes=1,
    data_collection_period=-1,     # solo interesa como quedo la partida al final
    display_progress=True,
)

df = pd.DataFrame(results)
df["gano"] = 0
for i in df.index:
    if df.loc[i, "Estado"] == "ganado":
        df.loc[i, "gano"] = 1

df.to_csv(os.path.join(carpeta, "resultados.csv"), index=False)
print("Listo:", len(df), "corridas guardadas en resultados.csv")
