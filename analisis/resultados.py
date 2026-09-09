# Saca la tabla comparativa y las graficas del csv que dejo correr_simulaciones.py
# Se corre asi:  python resultados.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

carpeta = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(carpeta, "resultados.csv"))

# ---------------------------------------------------------------------------
# La tabla que pide el reto: aleatoria contra mejorada
# ---------------------------------------------------------------------------
tabla = df.groupby(["estrategia", "avances", "rescatistas"]).agg(
    rescatados=("Rescatados", "mean"),
    perdidas=("Perdidas", "mean"),
    danio=("Danio", "mean"),
    rondas=("Pasos", "mean"),
    ganadas=("gano", "sum"),
    corridas=("gano", "count"),
)
tabla["porcentaje"] = (tabla["ganadas"] / tabla["corridas"]) * 100
print(tabla.round(2))
tabla.to_csv(os.path.join(carpeta, "tabla_resumen.csv"))

# ---------------------------------------------------------------------------
# Grafica 1: victimas rescatadas por estrategia
# ---------------------------------------------------------------------------
sns.set_theme(style="whitegrid")
fig, axis = plt.subplots(figsize=(7, 5))
sns.barplot(data=df, x="avances", y="Rescatados", hue="estrategia", ax=axis)
axis.set_title("Victimas rescatadas segun que tan rapido avanza el fuego")
axis.set_xlabel("avances de fuego por ronda")
axis.set_ylabel("victimas rescatadas")
plt.savefig(os.path.join(carpeta, "grafica_rescatados.png"), dpi=120)
plt.close()

# ---------------------------------------------------------------------------
# Grafica 2: partidas ganadas con la mejorada segun el reparto de roles
# ---------------------------------------------------------------------------
mejorada = df[df["estrategia"] == "mejorada"]
ganadas = mejorada.groupby(["avances", "rescatistas"])["gano"].sum().reset_index()

fig, axis = plt.subplots(figsize=(7, 5))
sns.barplot(data=ganadas, x="avances", y="gano", hue="rescatistas", ax=axis)
axis.set_title("Partidas ganadas de 30 con la estrategia mejorada")
axis.set_xlabel("avances de fuego por ronda")
axis.set_ylabel("partidas ganadas")
plt.savefig(os.path.join(carpeta, "grafica_ganadas.png"), dpi=120)
plt.close()

print("Listo: tabla_resumen.csv y las dos graficas quedaron en la carpeta analisis.")
