using UnityEngine;

public class PanelManager : MonoBehaviour
{
    public GameObject panelJuego;
    public GameObject panelVictimaRescatada;
    public GameObject panelVictimaAbatida;

    // cuanto tiempo se quedan los paneles de victima
    public float duracionPanel = 2f;

    void Start()
    {
        MostrarPanelJuego();
    }

    public void MostrarPanelJuego()
    {
        panelJuego.SetActive(true);
        panelVictimaRescatada.SetActive(false);
        panelVictimaAbatida.SetActive(false);
    }

    public void MostrarVictimaRescatada()
    {
        panelJuego.SetActive(false);
        panelVictimaRescatada.SetActive(true);
        panelVictimaAbatida.SetActive(false);

        CancelInvoke("MostrarPanelJuego");
        Invoke("MostrarPanelJuego", duracionPanel);
    }

    public void MostrarVictimaAbatida()
    {
        panelJuego.SetActive(false);
        panelVictimaRescatada.SetActive(false);
        panelVictimaAbatida.SetActive(true);

        CancelInvoke("MostrarPanelJuego");
        Invoke("MostrarPanelJuego", duracionPanel);
    }
}