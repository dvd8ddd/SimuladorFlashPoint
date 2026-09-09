using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class GameManager : MonoBehaviour
{
    public GameObject prefabParedIntacta;
    public GameObject prefabParedDanada;
    public GameObject prefabPuertaCerrada;
    public GameObject prefabPuertaAbierta;
    public GameObject prefabFuego;
    public GameObject prefabHumo;
    public GameObject prefabPoiTapado;   // se usa igual para valor 1 y valor 2
    public GameObject prefabVictima;     // solo para valor 3, ya revelada

    public GameObject[] prefabsBomberos; // tamano 6, uno por id (0 a 5)

    public TextMeshProUGUI textoRescatados;
    public TextMeshProUGUI textoInfectada;
    public TextMeshProUGUI textoDanio;
    public TextMeshProUGUI textoFormasPrimitivas;

    public float tamanoCelda = 1f;

    // cada cuantos segundos se pide el siguiente paso al servidor,
    // ajustalo en el Inspector para que se vea a un ritmo comodo
    public float segundosEntrePasos = 1.5f;

    // guarda todo lo que se instancia en un paso, para poder borrarlo
    // antes de dibujar el siguiente
    private List<GameObject> objetosInstanciados = new List<GameObject>();

    private WebClient cliente;
    private bool partidaTerminada = false;

    // que tan lejos del centro de la celda se coloca cada tipo,
    // ajustalos en el Inspector si la puerta y la pared tienen
    // distinta profundidad/grosor
    public float offsetPared = 0.5f;
    public float offsetPuerta = 0.5f;

    void Start()
    {
        cliente = GetComponent<WebClient>();
        StartCoroutine(cliente.PedirNuevaPartida(ProcesarEstadoNuevo));
    }

    void ProcesarEstadoNuevo(string textoJson)
    {
        EstadoData estado = JsonUtility.FromJson<EstadoData>(textoJson);
        LimpiarTablero();
        DibujarTablero(estado);
        ActualizarHUD(estado);

        if (estado.estado == "en_curso")
        {
            Invoke("PedirSiguientePaso", segundosEntrePasos);
        }
        else
        {
            partidaTerminada = true;
            Debug.Log("Partida terminada: " + estado.estado);
        }
    }

    void PedirSiguientePaso()
    {
        if (partidaTerminada)
        {
            return;
        }
        StartCoroutine(cliente.PedirSiguientePaso(ProcesarEstadoNuevo));
    }

    void LimpiarTablero()
    {
        for (int i = 0; i < objetosInstanciados.Count; i++)
        {
            Destroy(objetosInstanciados[i]);
        }
        objetosInstanciados.Clear();
    }

    Vector3 GridToWorld(int fila, int col)
    {
        float x = col * tamanoCelda;
        float z = -fila * tamanoCelda;
        return new Vector3(x, 0f, z);
    }

    void DibujarTablero(EstadoData estado)
    {
        // paredes: cada celda tiene 4 valores seguidos
        // direccion: 0 arriba, 1 izquierda, 2 abajo, 3 derecha
        for (int fila = 0; fila < 6; fila++)
        {
            for (int col = 0; col < 8; col++)
            {
                int baseIndice = (fila * 8 + col) * 4;

                // solo dibujamos arriba (0) e izquierda (1) de cada celda,
                // para no duplicar paredes que comparten dos celdas
                DibujarUnLado(estado.paredes[baseIndice + 0], fila, col, 0);
                DibujarUnLado(estado.paredes[baseIndice + 1], fila, col, 1);

                // la ultima fila necesita su lado de abajo (2)
                if (fila == 5)
                {
                    DibujarUnLado(estado.paredes[baseIndice + 2], fila, col, 2);
                }
                // la ultima columna necesita su lado derecho (3)
                if (col == 7)
                {
                    DibujarUnLado(estado.paredes[baseIndice + 3], fila, col, 3);
                }
            }
        }

        // fuego y humo
        for (int fila = 0; fila < 6; fila++)
        {
            for (int col = 0; col < 8; col++)
            {
                int indice = fila * 8 + col;
                int valorFuego = estado.fuego[indice];
                if (valorFuego == 1)
                {
                    GameObject obj = Instantiate(prefabHumo, GridToWorld(fila, col), Quaternion.identity);
                    objetosInstanciados.Add(obj);
                }
                else if (valorFuego == 2)
                {
                    GameObject obj = Instantiate(prefabFuego, GridToWorld(fila, col), Quaternion.identity);
                    objetosInstanciados.Add(obj);
                }
            }
        }

        // poi: 1 y 2 se ven IGUAL (marcador boca abajo, mismo prefab),
        // porque el jugador no debe poder distinguirlos con solo ver
        // el tablero. 3 es victima ya revelada, si es visualmente distinta.
        // OJO: una falsa alarma revelada nunca queda visible en el tablero,
        // poi.py la descarta directo (vuelve a valor 0), por eso no existe
        // un prefab de "falsa alarma revelada" aqui.
        for (int fila = 0; fila < 6; fila++)
        {
            for (int col = 0; col < 8; col++)
            {
                int indice = fila * 8 + col;
                int valorPoi = estado.poi[indice];
                if (valorPoi == 1 || valorPoi == 2)
                {
                    GameObject obj = Instantiate(prefabPoiTapado, GridToWorld(fila, col), Quaternion.identity);
                    objetosInstanciados.Add(obj);
                }
                else if (valorPoi == 3)
                {
                    GameObject obj = Instantiate(prefabVictima, GridToWorld(fila, col), Quaternion.identity);
                    objetosInstanciados.Add(obj);
                }
            }
        }

        // bomberos, cada uno con su propio modelo segun su id
        for (int i = 0; i < estado.bomberos.Length; i++)
        {
            BomberoData bombero = estado.bomberos[i];
            Vector3 posicion = GridToWorld(bombero.fila, bombero.col);
            GameObject prefabDeEsteBombero = prefabsBomberos[bombero.id];
            GameObject obj = Instantiate(prefabDeEsteBombero, posicion, Quaternion.identity);
            objetosInstanciados.Add(obj);
        }
    }

    void DibujarUnLado(int valor, int fila, int col, int direccion)
    {
        // 0 nada, 3 destruida, 6 puerta destruida -> no se dibuja nada
        if (valor == 0 || valor == 3 || valor == 6)
        {
            return;
        }

        // mismo offset base que las paredes, pero si valor es puerta
        // (4 o 5) usa el offset propio de puerta -> mismo patron
        // binario de rotacion que ya funcionaba para las paredes
        float offset = offsetPared;
        if (valor == 4 || valor == 5)
        {
            offset = offsetPuerta;
        }

        Vector3 posicion = GridToWorld(fila, col);
        Quaternion rotacion = Quaternion.identity;

        if (direccion == 0)
        {
            posicion += new Vector3(0f, 0f, offset);
        }
        else if (direccion == 1)
        {
            posicion += new Vector3(-offset, 0f, 0f);
            rotacion = Quaternion.Euler(0f, 90f, 0f);
        }
        else if (direccion == 2)
        {
            posicion += new Vector3(0f, 0f, -offset);
        }
        else if (direccion == 3)
        {
            posicion += new Vector3(offset, 0f, 0f);
            rotacion = Quaternion.Euler(0f, 90f, 0f);
        }

        GameObject objInstanciado = null;
        if (valor == 1)
        {
            objInstanciado = Instantiate(prefabParedIntacta, posicion, rotacion);
        }
        else if (valor == 2)
        {
            objInstanciado = Instantiate(prefabParedDanada, posicion, rotacion);
        }
        else if (valor == 4)
        {
            objInstanciado = Instantiate(prefabPuertaCerrada, posicion, rotacion);
        }
        else if (valor == 5)
        {
            objInstanciado = Instantiate(prefabPuertaAbierta, posicion, rotacion);
        }

        if (objInstanciado != null)
        {
            objetosInstanciados.Add(objInstanciado);
        }
    }

    void ActualizarHUD(EstadoData estado)
    {
        textoRescatados.text = estado.rescatados + " / 7";
        textoInfectada.text = estado.perdidas + " / 4";
        textoDanio.text = estado.danio + " / 24";

        // "Formas Primitivas Activas" no viene como numero directo en el
        // JSON, hay que contar cuantas casillas del arreglo fuego valen 2
        int contadorFuego = 0;
        for (int i = 0; i < estado.fuego.Length; i++)
        {
            if (estado.fuego[i] == 2)
            {
                contadorFuego += 1;
            }
        }
        textoFormasPrimitivas.text = contadorFuego.ToString();
    }
}