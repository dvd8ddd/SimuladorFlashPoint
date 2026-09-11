"""Análisis comparativo de las estrategias del simulador de Flash Point: Fire Rescue.

Este módulo consume los archivos CSV producidos por ``correr_simulaciones.py`` y genera
un reporte de texto en consola junto con tres visualizaciones orientadas a los criterios
de evaluación del reto.

    $ python resultados.py

Declarar uso de Inteligencia artificial
Este módulo y ``resultados.py`` fueron desarrollados con asistencia de
inteligencia artificial, específicamente en los siguientes aspectos:

    * La agregación y transformación de los DataFrames de pandas.
    * La construcción de las visualizaciones con seaborn y matplotlib.
    * El formato del reporte de texto impreso en consola.
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# --------------------------------------------------------------------------------
# CONFIGURACIÓN GLOBAL
# --------------------------------------------------------------------------------

CARPETA = os.path.dirname(os.path.abspath(__file__))

BOMBEROS = 6
AP_POR_TURNO = 4
VICTIMAS_PARA_GANAR = 7
DANIO_PARA_COLAPSO = 24

ANCHO_ETIQUETA = 26
ANCHO_VALOR = 10

sns.set_theme(style="whitegrid")


# --------------------------------------------------------------------------------
# UTILIDADES DE FORMATO
# --------------------------------------------------------------------------------

def imprimir_metrica(etiqueta: str, valor) -> None:
    """Imprime una métrica del reporte con las columnas alineadas.

    Args:
        etiqueta: Texto descriptivo que identifica la métrica.
        valor: Valor a mostrar; se convierte a cadena automáticamente.
    """
    print(f"{etiqueta:<{ANCHO_ETIQUETA}}{str(valor):>{ANCHO_VALOR}}")


def imprimir_titulo(titulo: str) -> None:
    """Imprime un encabezado de sección con el formato estándar del reporte.

    Args:
        titulo: Texto del encabezado, que será convertido a mayúsculas.
    """
    print(f"\n=== {titulo.upper()} ===")


# --------------------------------------------------------------------------------
# GENERACIÓN DEL REPORTE POR ESTRATEGIA
# --------------------------------------------------------------------------------

def generar_reporte(nombre: str, datos: pd.DataFrame) -> None:
    """Imprime el resumen estadístico completo de una estrategia.

    Args:
        nombre: Identificador de la estrategia ("aleatoria" o "mejorada").
        datos: Subconjunto del DataFrame con una fila por partida finalizada.
    """
    imprimir_titulo("estrategia " + nombre)

    total = len(datos)
    ganadas = int(datos["gano"].sum())
    porcentaje = 100 * ganadas / total

    imprimir_metrica("Partidas:", total)
    imprimir_metrica("Ganadas:", ganadas)
    imprimir_metrica("Perdidas:", total - ganadas)
    imprimir_metrica("Porcentaje de victoria:", f"{porcentaje:.1f}%")
    print()

    rondas = datos["Pasos"].mean()
    imprimir_metrica("Rondas promedio:", f"{rondas:.2f}")
    imprimir_metrica("Turnos de bombero:", f"{rondas * BOMBEROS:.2f}")
    imprimir_metrica("AP del equipo:", f"{rondas * BOMBEROS * AP_POR_TURNO:.2f}")
    print()

    metricas = {
        "Rescatados promedio:": "Rescatados",
        "Victimas perdidas:": "Perdidas",
        "Danio al edificio:": "Danio",
        "Celdas en llamas:": "Fuegos",
        "Paredes danadas:": "Paredes",
        "Puertas abiertas:": "Puertas",
    }
    for etiqueta, columna in metricas.items():
        imprimir_metrica(etiqueta, f"{datos[columna].mean():.2f}")
    print()

    print("Como termino:")
    conteo = datos["motivo"].value_counts()
    for motivo in ["victoria", "colapso", "victimas"]:
        print(f"  {motivo:<12}{conteo.get(motivo, 0):>6}")


def generar_comparativa(aleatoria: pd.DataFrame, mejorada: pd.DataFrame) -> None:
    """Imprime la tabla comparativa lado a lado entre ambas estrategias.

    Args:
        aleatoria: Partidas finalizadas de la estrategia aleatoria.
        mejorada: Partidas finalizadas de la estrategia mejorada.
    """
    imprimir_titulo("aleatoria contra mejorada")
    cabecera = "aleatoria".rjust(ANCHO_VALOR) + "mejorada".rjust(ANCHO_VALOR)
    print(" " * ANCHO_ETIQUETA + cabecera)

    filas = [
        ("Porcentaje de victoria:", "gano", 100),
        ("Rescatados promedio:", "Rescatados", 1),
        ("Victimas perdidas:", "Perdidas", 1),
        ("Danio al edificio:", "Danio", 1),
        ("Celdas en llamas:", "Fuegos", 1),
        ("Paredes danadas:", "Paredes", 1),
        ("Puertas abiertas:", "Puertas", 1),
        ("Rondas que aguanta:", "Pasos", 1),
    ]
    for etiqueta, columna, escala in filas:
        valor_a = aleatoria[columna].mean() * escala
        valor_m = mejorada[columna].mean() * escala
        print(f"{etiqueta:<{ANCHO_ETIQUETA}}{valor_a:>{ANCHO_VALOR}.2f}{valor_m:>{ANCHO_VALOR}.2f}")


# --------------------------------------------------------------------------------
# VISUALIZACIONES
# --------------------------------------------------------------------------------

def etiquetar(ejes, formato: str = "%.2f") -> None:
    """Escribe el valor numerico encima de cada barra de un eje.

    Args:
        ejes: Eje de matplotlib que contiene los contenedores de barras.
        formato: Cadena de formato aplicada al valor de cada barra.
    """
    for contenedor in ejes.containers:
        ejes.bar_label(contenedor, fmt=formato, fontsize=9, padding=2)


def graficar_resultado(datos: pd.DataFrame) -> None:
    """Genera la comparativa principal entre ambas estrategias.

    El panel izquierdo muestra las victimas rescatadas por partida contra el umbral de
    victoria. El panel derecho muestra el porcentaje de partidas ganadas. Ambas
    estrategias corren con el mismo reparto de roles que utiliza el simulador.

    Args:
        datos: DataFrame con una fila por partida finalizada.
    """
    victorias = datos.groupby("estrategia")["gano"].mean().mul(100).reset_index()

    figura, (izquierda, derecha) = plt.subplots(1, 2, figsize=(11, 5))

    sns.barplot(data=datos, x="estrategia", y="Rescatados", hue="estrategia",
                errorbar=None, legend=False, ax=izquierda)
    izquierda.axhline(VICTIMAS_PARA_GANAR, color="black", linestyle="--", linewidth=1)
    izquierda.text(-0.45, VICTIMAS_PARA_GANAR + 0.15, "7 rescatadas = victoria",
                   fontsize=9)
    izquierda.set_ylim(0, 8)
    izquierda.set_title("Victimas rescatadas por partida")
    izquierda.set_xlabel("")
    izquierda.set_ylabel("victimas rescatadas")
    etiquetar(izquierda, "%.2f")

    sns.barplot(data=victorias, x="estrategia", y="gano", hue="estrategia",
                errorbar=None, legend=False, ax=derecha)
    derecha.set_ylim(0, 100)
    derecha.set_title("Porcentaje de partidas ganadas")
    derecha.set_xlabel("")
    derecha.set_ylabel("partidas ganadas (%)")
    etiquetar(derecha, "%.1f%%")

    figura.savefig(os.path.join(CARPETA, "grafica_rescatados.png"), dpi=120,
                   bbox_inches="tight")
    plt.close(figura)


def graficar_roles(datos: pd.DataFrame, por_ronda: pd.DataFrame) -> None:
    """Contrasta el reparto inicial de roles contra el reparto efectivo y las victorias.

    El panel izquierdo compara cuántos bomberos arrancan con rol de rescate contra
    cuántos lo ejercen realmente, promediado sobre todas las rondas de todas las
    partidas. El panel derecho muestra las victorias obtenidas en cada caso. La lectura
    conjunta evidencia que incrementar el número inicial de rescatistas no incrementa el
    esfuerzo de rescate efectivo, pero sí degrada el desempeño global.

    Args:
        datos: DataFrame con una fila por partida finalizada.
        por_ronda: DataFrame con una fila por ronda de cada partida.
    """
    finales = datos[datos["estrategia"] == "mejorada"]
    rondas = por_ronda[por_ronda["estrategia"] == "mejorada"]
    corridas = int(finales.groupby("rescatistas").size().max())

    efectivo = rondas.groupby("rescatistas")["Rescatando"].mean().reset_index()
    efectivo = efectivo.rename(columns={"Rescatando": "cantidad"})
    efectivo["momento"] = "rescatando de verdad"

    inicial = pd.DataFrame({
        "rescatistas": efectivo["rescatistas"],
        "cantidad": efectivo["rescatistas"].astype(float),
        "momento": "asignados al arrancar",
    })
    comparacion = pd.concat([inicial, efectivo], ignore_index=True)
    ganadas = finales.groupby("rescatistas")["gano"].sum().reset_index()

    figura, (izquierda, derecha) = plt.subplots(1, 2, figsize=(11, 5))

    sns.barplot(data=comparacion, x="rescatistas", y="cantidad", hue="momento",
                errorbar=None, ax=izquierda)
    izquierda.set_title("Cuantos bomberos rescatan en realidad")
    izquierda.set_xlabel("bomberos que arrancan con rol de rescate (de 6)")
    izquierda.set_ylabel("bomberos rescatando, promedio por ronda")
    izquierda.legend(title="")
    etiquetar(izquierda)

    sns.barplot(data=ganadas, x="rescatistas", y="gano", color="tab:orange",
                errorbar=None, ax=derecha)
    derecha.set_title(f"Partidas ganadas de {corridas}")
    derecha.set_xlabel("bomberos que arrancan con rol de rescate (de 6)")
    derecha.set_ylabel("partidas ganadas")
    etiquetar(derecha, "%d")

    figura.savefig(os.path.join(CARPETA, "grafica_roles.png"), dpi=120,
                   bbox_inches="tight")
    plt.close(figura)


def graficar_danio_por_ronda(por_ronda: pd.DataFrame) -> None:
    """Genera la curva de daño estructural acumulado a lo largo de la partida.

    Args:
        por_ronda: DataFrame con una fila por ronda de cada partida.
    """
    figura, ejes = plt.subplots(figsize=(7, 5))
    sns.lineplot(data=por_ronda, x="Step", y="Danio", hue="estrategia",
                 errorbar=None, ax=ejes)
    ejes.axhline(DANIO_PARA_COLAPSO, color="black", linestyle="--", linewidth=1)
    ejes.text(1.2, DANIO_PARA_COLAPSO + 0.4, "24 = el edificio colapsa", fontsize=9)
    ejes.set_xlim(1, 20)
    ejes.set_title("Danio estructural acumulado ronda por ronda")
    ejes.set_xlabel("ronda")
    ejes.set_ylabel("puntos de danio")
    figura.savefig(os.path.join(CARPETA, "grafica_danio.png"), dpi=120,
                   bbox_inches="tight")
    plt.close(figura)


def graficar_mecanismo(datos: pd.DataFrame) -> None:
    """Genera la comparación de paredes destruidas contra puertas utilizadas.

    Args:
        datos: DataFrame con una fila por partida finalizada.
    """
    largo = datos.melt(id_vars=["estrategia"], value_vars=["Paredes", "Puertas"],
                       var_name="elemento", value_name="cantidad")
    largo["elemento"] = largo["elemento"].replace({
        "Paredes": "paredes danadas",
        "Puertas": "puertas abiertas",
    })

    figura, ejes = plt.subplots(figsize=(7, 5))
    sns.barplot(data=largo, x="elemento", y="cantidad", hue="estrategia",
                errorbar=None, ax=ejes)
    ejes.set_title("Como trata cada estrategia el edificio")
    ejes.set_xlabel("")
    ejes.set_ylabel("promedio por partida")
    etiquetar(ejes)
    figura.savefig(os.path.join(CARPETA, "grafica_mecanismo.png"), dpi=120,
                   bbox_inches="tight")
    plt.close(figura)


# --------------------------------------------------------------------------------
# PUNTO DE ENTRADA
# --------------------------------------------------------------------------------

def main() -> None:
    """Orquesta la carga de datos, la impresion del reporte y el guardado de graficas."""
    datos = pd.read_csv(os.path.join(CARPETA, "resultados.csv"))
    por_ronda = pd.read_csv(os.path.join(CARPETA, "por_ronda.csv"))
    roles = pd.read_csv(os.path.join(CARPETA, "resultados_roles.csv"))
    por_ronda_roles = pd.read_csv(os.path.join(CARPETA, "por_ronda_roles.csv"))

    aleatoria = datos[datos["estrategia"] == "aleatoria"]
    mejorada = datos[datos["estrategia"] == "mejorada"]

    generar_reporte("aleatoria", aleatoria)
    generar_reporte("mejorada", mejorada)
    generar_comparativa(aleatoria, mejorada)

    resumen = datos.groupby("estrategia").agg(
        rescatados=("Rescatados", "mean"),
        perdidas=("Perdidas", "mean"),
        danio=("Danio", "mean"),
        rondas=("Pasos", "mean"),
        ganadas=("gano", "sum"),
        corridas=("gano", "count"),
    )
    resumen["porcentaje"] = 100 * resumen["ganadas"] / resumen["corridas"]
    resumen.to_csv(os.path.join(CARPETA, "tabla_resumen.csv"))

    tabla = roles.groupby("rescatistas").agg(
        rescatados=("Rescatados", "mean"),
        perdidas=("Perdidas", "mean"),
        danio=("Danio", "mean"),
        rondas=("Pasos", "mean"),
        ganadas=("gano", "sum"),
        corridas=("gano", "count"),
    )
    tabla["porcentaje"] = 100 * tabla["ganadas"] / tabla["corridas"]

    imprimir_titulo("por reparto de roles (solo estrategia mejorada)")
    print(tabla.round(2))
    tabla.to_csv(os.path.join(CARPETA, "tabla_roles.csv"))

    graficar_resultado(datos)
    graficar_roles(roles, por_ronda_roles)
    graficar_danio_por_ronda(por_ronda)
    graficar_mecanismo(datos)

    print()
    print("Listo: tabla_resumen.csv, tabla_roles.csv y las cuatro graficas quedaron "
          "en la carpeta analisis.")


if __name__ == "__main__":
    main()
