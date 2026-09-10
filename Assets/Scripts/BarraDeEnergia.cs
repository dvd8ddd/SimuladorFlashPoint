using UnityEngine;

public class BarraDeEnergia : MonoBehaviour
{
    // Solo para habilitar/deshabilitar los puntos de energia de cada agente
    public GameObject[] rayos;

    public void MostrarCantidad(int cantidad)
    {
        for (int i = 0; i < rayos.Length; i++)
        {
            if (i < cantidad)
            {
                rayos[i].SetActive(true);
            }
            else
            {
                rayos[i].SetActive(false);
            }
        }
    }
}