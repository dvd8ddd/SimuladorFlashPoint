using System.IO;
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

    void Start()
    {
        // Busca en Assets/StreamingAssets el .json, lo lee, convierte a string y se usa para crear los gameobjects.
        string ruta = Application.streamingAssetsPath + "/estado_ejemplo.json";
        string texto = File.ReadAllText(ruta);
        EstadoData estado = JsonUtility.FromJson<EstadoData>(texto);
        DibujarTablero(estado);
        ActualizarHUD(estado);
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
                    Instantiate(prefabHumo, GridToWorld(fila, col), Quaternion.identity);
                }
                else if (valorFuego == 2)
                {
                    Instantiate(prefabFuego, GridToWorld(fila, col), Quaternion.identity);
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
                    Instantiate(prefabPoiTapado, GridToWorld(fila, col), Quaternion.identity);
                }
                else if (valorPoi == 3)
                {
                    Instantiate(prefabVictima, GridToWorld(fila, col), Quaternion.identity);
                }
            }
        }

        // bomberos, cada uno con su propio modelo segun su id
        for (int i = 0; i < estado.bomberos.Length; i++)
        {
            BomberoData bombero = estado.bomberos[i];
            Vector3 posicion = GridToWorld(bombero.fila, bombero.col);
            GameObject prefabDeEsteBombero = prefabsBomberos[bombero.id];
            Instantiate(prefabDeEsteBombero, posicion, Quaternion.identity);
        }
    }

    void DibujarUnLado(int valor, int fila, int col, int direccion)
    {
        // 0 nada, 3 destruida, 6 puerta destruida -> no se dibuja nada
        if (valor == 0 || valor == 3 || valor == 6)
        {
            return;
        }

        Vector3 posicion = GridToWorld(fila, col);
        Quaternion rotacion = Quaternion.identity;

        // ajusta la posicion/rotacion segun el lado, esto depende
        // de como esten armados tus prefabs de pared
        if (direccion == 0)
        {
            posicion += new Vector3(0f, 0f, tamanoCelda * 0.5f);
        }
        else if (direccion == 1)
        {
            posicion += new Vector3(-tamanoCelda * 0.5f, 0f, 0f);
            rotacion = Quaternion.Euler(0f, 90f, 0f);
        }
        else if (direccion == 2)
        {
            posicion += new Vector3(0f, 0f, -tamanoCelda * 0.5f);
        }
        else if (direccion == 3)
        {
            posicion += new Vector3(tamanoCelda * 0.5f, 0f, 0f);
            rotacion = Quaternion.Euler(0f, 90f, 0f);
        }

        if (valor == 1)
        {
            Instantiate(prefabParedIntacta, posicion, rotacion);
        }
        else if (valor == 2)
        {
            Instantiate(prefabParedDanada, posicion, rotacion);
        }
        else if (valor == 4)
        {
            Instantiate(prefabPuertaCerrada, posicion, rotacion);
        }
        else if (valor == 5)
        {
            Instantiate(prefabPuertaAbierta, posicion, rotacion);
        }
    }

    void ActualizarHUD(EstadoData estado)
    {
        textoRescatados.text = estado.rescatados + " / 7";
        textoInfectada.text = estado.perdidas + " / 4";
        textoDanio.text = estado.danio + " / 24";

        // "Fuego" no viene como numero directo en el
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