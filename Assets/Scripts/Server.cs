using System.Collections.Generic;
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System;
using System.Text;

public class Server : MonoBehaviour
{
    static int port = 9090;
    static string addr = "127.0.0.1";

    Socket listenSocket;
    bool connected = false;

    System.Threading.Thread SocketThread;
    bool listenerFlag = false;


    public GameObject Car;
    Car_Controller car_controller;


    // Start is called before the first frame update
    void Start()
    {
        car_controller = Car.gameObject.GetComponent<Car_Controller>();

        InitServer();
    }

    void InitServer()
    {
        IPEndPoint ipPoint = new IPEndPoint(IPAddress.Parse(addr), port);
        listenSocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        try
        {
            listenSocket.Bind(ipPoint);
            listenSocket.Listen(1);
            connected = true;
            Debug.Log("Сервер запущен. Ожидание подключений...");
            Application.runInBackground = true;
            listenerFlag = true;
            startServer();
        }
        catch (Exception ex)
        {
            Debug.Log(ex.Message);
        }
    }

    void startServer()
    {
        SocketThread = new System.Threading.Thread(ListenerThread);
        SocketThread.IsBackground = true;
        SocketThread.Start();
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.P))
        {
            if (SocketThread.IsAlive)
            {
                listenerFlag = false;
                listenSocket.Close();
                SocketThread.Abort();
                Debug.Log("!!!!!!!!!!!Сервер остановлен!!!!!!!!!!!");
            }
            else
            {
                IPEndPoint ipPoint = new IPEndPoint(IPAddress.Parse(addr), port);
                listenSocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
                try
                {
                    listenSocket.Bind(ipPoint);
                    listenSocket.Listen(1);
                    connected = true;
                    Debug.Log("Сервер запущен. Ожидание подключений...");
                    Application.runInBackground = true;
                    listenerFlag = true;
                    startServer();
                }
                catch (Exception ex)
                {
                    Debug.Log(ex.Message);
                }
            }
        }
    }

    void ListenerThread()
    {
        
        if (connected)
        {
            Socket handler = listenSocket.Accept();
            Debug.Log("Клиент подключен");
            while (listenerFlag)
            {
                // получаем сообщение
                StringBuilder builder = new StringBuilder();
                int bytes = 0; // количество полученных байтов
                byte[] data = new byte[256]; // буфер для получаемых данных
                do
                {
                    bytes = handler.Receive(data);
                    builder.Append(Encoding.UTF8.GetString(data, 0, bytes));
                }
                while (handler.Available > 0);

                Debug.Log(DateTime.Now.ToShortTimeString() + ": " + builder.ToString());

                //Sending png
                byte[] data_png = car_controller.PngFromCam;
                handler.Send(data_png);

                //Sending JSON
                Dictionary<string, string> dict_data = new Dictionary<string, string>
                {
                    ["ID"] = 0.ToString(),
                    ["CurrentSpeed"] = car_controller.CurrentSpeed.ToString(),
                    ["CurrentSteering"] = car_controller.CurrentSteering.ToString()
                };
                //
                //    "{" +
                //    "\"ID\"" + ":" +              "\""+0.ToString()+"\""+","+
                //    "\"CurrentSpeed\"" + ":" +    "\""+car_controller.CurrentSpeed.ToString()+ "\"" + "," +
                //    "\"CurrentSteering\"" + ":" +  "\""+car_controller.CurrentSteering.ToString()+ "\"" + "" +
                //    "}";
                string json = DictToJson(dict_data);
                Debug.Log(json);
                byte[] data_json = Encoding.UTF8.GetBytes(json);
                handler.Send(data_json);

                //// отправляем ответ
                //string message = "ваше сообщение доставлено";
                //data = Encoding.UTF8.GetBytes(message);
                //handler.Send(data);
            }
        }
    }


    string DictToJson(Dictionary<string, string> dict)
    {
        string json = "";
        string[] list = new string[dict.Count];
        json += "{";

        int k = 0;
        foreach(string i in dict.Keys)
        {
            list[k] = string.Format("\"{0}\" : \"{1}\"", i, dict[i]);
            k++;
        }
        json += string.Join(",", list);
        
        json += "}";

        return json;
    }
}
