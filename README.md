# SimuladorFlashPoint

Simulación multiagente de Flash Point: Fire Rescue, ambientada en el universo de Halo. Backend en Python con Mesa, visualización en Unity conectada por HTTP/JSON.

## Estructura del repo

```
SimulacionAvanzada/   estrategia aleatoria y estrategia mejorada (Dijkstra, roles fijos) | las dos viven aqui, es lo que compara analisis/
SimulacionBasica/     version inicial, no integrada | la comparacion final usa SimulacionAvanzada/
server/               servidor HTTP que conecta el modelo con Unity
analisis/             corridas comparativas y gráficas (aleatoria vs. mejorada)
tableros/             tablero del juego y estado de ejemplo para pruebas sin servidor
Diagramas de Estado/  diagramas de la partida, el bombero y el tablero
```

El proyecto de Unity vive en la rama `ModeloSimulador`.

## Cómo correrlo

**Backend:**
```bash
pip install mesa numpy networkx
cd server
python server.py 8585
```

**Unity:** con el servidor corriendo, abrir el proyecto (rama `ModeloSimulador`) y darle Play. Se conecta a `http://localhost:8585`.
Un GET reinicia la partida, cada POST avanza un turno.

**Simulaciones comparativas:**
```bash
pip install pandas matplotlib seaborn
cd analisis
python correr_simulaciones.py
python resultados.py
```

## Documentación

- `Diagramas de Estado/` — los 3 diagramas de estado del proyecto

## Equipo

David — tablero y estrategia aleatoria · 

Sergio — estrategia mejorada, servidor y análisis · 

Facundo — Unity, narrativa y diagramas