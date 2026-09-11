"""Ejecución masiva de simulaciones de Flash Point: Fire Rescue mediante ``batch_run``.

Este módulo ejecuta ambas estrategias bajo las condiciones del reglamento y persiste los
resultados en dos archivos CSV que posteriormente consume ``resultados.py``.

    $ python correr_simulaciones.py

Se ejecutan dos barridos independientes:

    1. Comparativa principal. Ambas estrategias bajo la configuracion que el simulador
       utiliza en produccion (dos bomberos asignados a rescate), con mil repeticiones
       por estrategia.
    2. Barrido de reparto de roles. Unicamente la estrategia mejorada, variando cuantos
       bomberos arrancan asignados a rescate. Documenta el proceso experimental que
       llevo a fijar el valor en dos.

Archivos generados:

    resultados.csv        Una fila por partida de la comparativa principal.
    por_ronda.csv         Una fila por ronda de cada partida de la comparativa.
    resultados_roles.csv  Una fila por partida del barrido de reparto de roles.
    por_ronda_roles.csv   Una fila por ronda de cada partida del barrido de roles.

Declarar uso de Inteligencia artificial
Este módulo y ``resultados.py`` fueron desarrollados con asistencia de
inteligencia artificial, específicamente en los siguientes aspectos:

    * La parametrización del barrido de configuraciones con ``batch_run``.
    * La agregación y transformación de los DataFrames de pandas.
    * La construcción de las visualizaciones con seaborn y matplotlib.
"""

import os
import sys
import time

import numpy as np
import pandas as pd
from mesa.batchrunner import batch_run

CARPETA = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CARPETA, "..", "SimulacionAvanzada"))

from modelo import FlashPointModel

# --------------------------------------------------------------------------------
# PARÁMETROS DEL EXPERIMENTO
# --------------------------------------------------------------------------------

MAX_PASOS = 200
CORRIDAS = 1000
CORRIDAS_ROLES = 300
SEMILLA_MAESTRA = 42
RESCATISTAS_PRODUCCION = 2
TABLERO = os.path.join(CARPETA, "..", "tableros", "tablero_final.txt")

# ``avances`` queda fijo en 1: el reglamento indica que el fuego avanza una vez al
# término del turno de cada bombero, y el modelo lo aplica dentro del turno, no al
# cerrar la ronda. Con seis bomberos la ronda completa suma seis avances.
#
# ``rescatistas`` queda fijo en 2 en la comparativa principal porque es el valor con el
# que corre el simulador y el servidor. Promediar los tres repartos penalizaría a la
# estrategia mejorada con dos configuraciones que fueron descartadas. La estrategia
# aleatoria ignora por completo el campo ``papel``, de modo que fijar el reparto no
# altera sus resultados y la comparación se mantiene pareja.
PARAMETROS = {
    "estrategia": ["aleatoria", "mejorada"],
    "avances": 1,
    "rescatistas": RESCATISTAS_PRODUCCION,
    "ruta": TABLERO,
}

# Barrido secundario: sostiene la decisión de haber fijado el reparto en dos.
PARAMETROS_ROLES = {
    "estrategia": "mejorada",
    "avances": 1,
    "rescatistas": [2, 3, 4],
    "ruta": TABLERO,
}


# --------------------------------------------------------------------------------
# EJECUCIÓN
# --------------------------------------------------------------------------------

def obtener_semillas(cantidad: int) -> list:
    """Deriva una lista de semillas reproducibles a partir de la semilla maestra.

    Args:
        cantidad: Número de semillas a generar, una por repetición.

    Returns:
        Lista de enteros utilizable como argumento ``rng`` de ``batch_run``.
    """
    generador = np.random.default_rng(SEMILLA_MAESTRA)
    return generador.integers(0, sys.maxsize, size=(cantidad,)).tolist()


def clasificar_desenlace(df: pd.DataFrame) -> pd.DataFrame:
    """Añade las columnas derivadas ``gano`` y ``motivo`` al DataFrame de resultados.

    Args:
        df: DataFrame con una fila por partida finalizada.

    Returns:
        El mismo DataFrame con las dos columnas añadidas.
    """
    df["gano"] = (df["Estado"] == "ganado").astype(int)
    df["motivo"] = np.where(
        df["Estado"] == "ganado", "victoria",
        np.where(df["Perdidas"] >= 4, "victimas", "colapso"),
    )
    return df


def ejecutar_barrido(parametros: dict, corridas: int, sufijo: str) -> pd.DataFrame:
    """Ejecuta un barrido de ``batch_run`` y persiste sus dos archivos CSV.

    Args:
        parametros: Diccionario de parametros en el formato que espera ``batch_run``.
        corridas: Numero de repeticiones por combinacion de parametros.
        sufijo: Texto que se agrega al nombre de los archivos de salida. Cadena vacia
            para la comparativa principal.

    Returns:
        DataFrame con una fila por partida finalizada.
    """
    resultados = batch_run(
        FlashPointModel,
        parameters=parametros,
        rng=obtener_semillas(corridas),
        max_steps=MAX_PASOS,
        number_processes=1,
        data_collection_period=1,
        display_progress=True,
    )
    df = pd.DataFrame(resultados)

    # La columna Grid contiene la matriz completa del tablero y numpy la serializa con
    # saltos de línea internos, lo que vuelve ilegible el CSV. La columna ruta expone la
    # estructura de directorios local. Ninguna de las dos interviene en el análisis.
    df = df.drop(columns=["Grid", "ruta"])

    # ``revisar_fin`` invoca al DataCollector una segunda vez al terminar la partida, de
    # modo que la última ronda aparece duplicada y sesgaría los promedios temporales.
    por_ronda = df.drop_duplicates(subset=["RunId", "Step"], keep="last")
    por_ronda.to_csv(os.path.join(CARPETA, f"por_ronda{sufijo}.csv"), index=False)

    finales = por_ronda.sort_values("Step").groupby("RunId").tail(1)
    finales = clasificar_desenlace(finales.copy())
    finales.to_csv(os.path.join(CARPETA, f"resultados{sufijo}.csv"), index=False)

    return finales


def main() -> None:
    """Ejecuta los dos barridos y guarda los cuatro archivos CSV de salida."""
    inicio = time.time()

    print()
    print(f"Comparativa principal: {CORRIDAS} partidas por estrategia, "
          f"{RESCATISTAS_PRODUCCION} bomberos asignados a rescate")
    principal = ejecutar_barrido(PARAMETROS, CORRIDAS, "")

    print()
    print(f"Barrido de reparto de roles: {CORRIDAS_ROLES} partidas por reparto")
    roles = ejecutar_barrido(PARAMETROS_ROLES, CORRIDAS_ROLES, "_roles")

    tardo = time.time() - inicio
    total = len(principal) + len(roles)

    print()
    print(f"Listo: {len(principal)} partidas en resultados.csv")
    print(f"       {len(roles)} partidas en resultados_roles.csv")
    print(f"Tardo {tardo:.1f} segundos, es decir {tardo / total:.3f} s por partida")
    print(f"Las semillas derivan de default_rng({SEMILLA_MAESTRA}), por lo que una nueva "
          f"ejecucion produce resultados identicos")


if __name__ == "__main__":
    main()
