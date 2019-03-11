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

        car_controller.UnderAI = true;

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
        while (true)
        {
            try
            {
                car_controller.TargetSpeed = 0;
                Debug.Log("Сервер запущен. Ожидание подключений...");
                Socket handler = listenSocket.Accept();
                Debug.Log("Клиент подключен");
                Debug.Log(handler.RemoteEndPoint);
                while (listenerFlag)
                {
                    //Recieve request
                    StringBuilder builder = new StringBuilder();
                    int bytes = 0; // количество полученных байтов
                    byte[] data = new byte[256]; // буфер для получаемых данных
                    do
                    {
                        bytes = handler.Receive(data);
                        builder.Append(Encoding.UTF8.GetString(data, 0, bytes));
                    }
                    while (handler.Available > 0);
                    Debug.Log(builder.ToString());

                    //Sending png
                    byte[] data_png = car_controller.PngFromCam;
                    handler.Send(data_png);

                    //Sending JSON
                    Dictionary<string, string> dict_data = new Dictionary<string, string>
                    {
                        ["ID"] = 0.ToString(),
                        ["CurrentSpeed"] = Math.Round(car_controller.CurrentSpeed, 1).ToString(),
                        ["CurrentSteering"] = Math.Round(car_controller.CurrentSteering, 1).ToString()
                    };
                    string json = MiniJSON.Json.Serialize(dict_data);
                    Debug.Log(json);
                    byte[] data_json = Encoding.UTF8.GetBytes(json);
                    handler.Send(data_json);

                    //Recieve datas
                    builder = new StringBuilder();
                    bytes = 0; // количество полученных байтов
                    data = new byte[256]; // буфер для получаемых данных
                    do
                    {
                        bytes = handler.Receive(data);
                        builder.Append(Encoding.UTF8.GetString(data, 0, bytes));
                    }
                    while (handler.Available > 0);
                    try
                    {
                        var json2 = builder.ToString();
                        var dict = MiniJSON.Json.Deserialize(json2) as Dictionary<string, object>;
                        car_controller.TargetSpeed = Convert.ToInt32(dict["speed"]);
                        //car_controller.TargetSteering = Convert.ToInt32(dict["steering"]);
                        Debug.Log(car_controller.TargetSteering);
                    }
                    catch { }

                    //Send answer
                    string resp = "OK";
                    data_json = Encoding.UTF8.GetBytes(resp);
                    handler.Send(data_json);

                }
            }
            catch(SocketException e)
            {
                Debug.Log(e.Message);
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
