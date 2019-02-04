using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[System.Serializable]
public class AP_Point
{
    public GameObject point;
    public int _state;
    public int State
    {
        get
        {
            return _state;
        }
        set
        {
            _state = value;
            switch (value)
            {
                case 0:
                    point.GetComponent<MeshRenderer>().material.color = Color.white; //обычный
                    break;
                case 1:
                    point.GetComponent<MeshRenderer>().material.color = Color.magenta; //следующий
                    break;
                case 2:
                    point.GetComponent<MeshRenderer>().material.color = Color.green; //текущий
                    break;
            }
        }
    }

    public AP_Point(GameObject go)
    {
        point = go;
        State = 0;
    }
}


public class Autopilot : MonoBehaviour
{

    public Car_Controller controlled_car;

    public List<AP_Point> points;

    public float k = 1;

    int curr = 0;
    int next = 1;

    // Start is called before the first frame update
    void Start()
    {
        controlled_car.UnderAI = true;
        controlled_car.TargetSpeed = 10;

        for (int i = 0; i < 50; i++)
        {
            Transform go = transform.Find("point (" + i + ")");
            if (go != null) points.Add(new AP_Point(go.gameObject));
        }

        points[next].State = 1;
        points[curr].State = 2;
    }
    

    void GenNextPair()
    {
        if (curr + 1 < points.Count) curr++;
        else curr = 0;

        if (next + 1 < points.Count) next++;
        else next = 0;
    }

    // Update is called once per frame
    void Update()
    {
        if(Vector3.Distance(points[curr].point.transform.position, controlled_car.transform.position) > 3)
        {
            Vector3 obj_pos = controlled_car.gameObject.transform.position;
            Vector3 cam_pos = controlled_car.camera.gameObject.transform.position;
            Vector3 point_pos = points[curr].point.gameObject.transform.position;
            Vector3 next_point_pos = points[next].point.gameObject.transform.position;

            Vector3 LW = controlled_car.truck_Infos[0].leftWheelMesh.gameObject.transform.position;
            Vector3 RW = controlled_car.truck_Infos[0].rightWheelMesh.gameObject.transform.position;
            float a = Vector2.Angle(new Vector2(cam_pos.x - obj_pos.x, cam_pos.z - obj_pos.z), new Vector2(point_pos.x - obj_pos.x, point_pos.z - obj_pos.z));
            //float b = Vector2.Angle(new Vector2(cam_pos.x - obj_pos.x, cam_pos.z - obj_pos.z), new Vector2(next_point_pos.x - obj_pos.x, next_point_pos.z - obj_pos.z));
            if (Vector3.Distance(point_pos, LW) >= Vector3.Distance(point_pos, RW))
            {
                controlled_car.TargetSteering = k * a;
            }
            else
            {
                controlled_car.TargetSteering = -1 * k * a;
            }
        }
        else
        {
            points[curr].State = 0;

            GenNextPair();
            points[curr].State = 2;
            points[next].State = 1;

        }
    }

}
