using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

public class WebClient : MonoBehaviour
{
    public string urlServidor = "http://localhost:8585";

    // GET reinicia la partida del lado del servidor. Se usa una sola
    // vez, cuando arranca la escena.
    public IEnumerator PedirNuevaPartida(System.Action<string> callback)
    {
        UnityWebRequest peticion = UnityWebRequest.Get(urlServidor);
        yield return peticion.SendWebRequest();

        if (peticion.result != UnityWebRequest.Result.Success)
        {
            Debug.Log("Error al pedir nueva partida: " + peticion.error);
        }
        else
        {
            callback(peticion.downloadHandler.text);
        }
    }

    // POST avanza una ronda. El servidor ignora lo que se manda en el
    // cuerpo, nomas necesita que el metodo sea POST.
    public IEnumerator PedirSiguientePaso(System.Action<string> callback)
    {
        byte[] cuerpo = Encoding.UTF8.GetBytes("");
        UnityWebRequest peticion = new UnityWebRequest(urlServidor, "POST");
        peticion.uploadHandler = new UploadHandlerRaw(cuerpo);
        peticion.downloadHandler = new DownloadHandlerBuffer();
        peticion.SetRequestHeader("Content-Type", "application/json");

        yield return peticion.SendWebRequest();

        if (peticion.result != UnityWebRequest.Result.Success)
        {
            Debug.Log("Error al pedir siguiente paso: " + peticion.error);
        }
        else
        {
            callback(peticion.downloadHandler.text);
        }
    }
}