using UnityEngine;

[System.Serializable]
public class BomberoData
{
    public int id;
    public int fila;
    public int col;
    public bool cargando;
}

[System.Serializable]
public class EstadoData
{
    public int paso;
    public string estado;
    public BomberoData[] bomberos;
    public int[] fuego;
    public int[] poi;
    public int[] paredes;
    public int rescatados;
    public int perdidas;
    public int danio;
}