using UnityEngine;
using System.Collections;
using System.Collections.Generic;

[System.Serializable]
public class Dot_Truck : System.Object
{
	public WheelCollider leftWheel;
	public GameObject leftWheelMesh;
	public WheelCollider rightWheel;
	public GameObject rightWheelMesh;
	public bool motor;
	public bool steering;
	public bool reverseTurn; 
}

[System.Serializable]
public class PID
{
    public float Kp = 0;
    public float Ki = 0;
    public float Kd = 0;

    public float P = 0;
    public float I = 0;
    public float D = 0;

    public float error = 0;
    public float previousError = 0;
}

public class Car_Controller : MonoBehaviour {

	public float maxMotorTorque;
	public float maxSteeringAngle;
    public float SteeringPower;
    public float TargetSteering;
    public float CurrentSteering;
    public bool UnderAI = false;
    public float TargetSpeed = 0;
    public float CurrentSpeed;
    public PID pid = new PID();

    public RenderTexture rt;
    Texture2D png_tex;
    public Camera camera;
    public byte[] PngFromCam;
    public List<Dot_Truck> truck_Infos;

    public void Start()
    {
        png_tex = new Texture2D(512, 512, TextureFormat.ARGB32, false);
        CurrentSteering = 0;
    }

    public void VisualizeWheel(Dot_Truck wheelPair)
	{
		Quaternion rot;
		Vector3 pos;
		wheelPair.leftWheel.GetWorldPose ( out pos, out rot);
		wheelPair.leftWheelMesh.transform.position = pos;
		wheelPair.leftWheelMesh.transform.rotation = rot;
		wheelPair.rightWheel.GetWorldPose ( out pos, out rot);
		wheelPair.rightWheelMesh.transform.position = pos;
		wheelPair.rightWheelMesh.transform.rotation = rot;
	}

	public void Update()
	{
        RenderTextureToPng();
        CurrentSpeed = gameObject.GetComponent<Rigidbody>().velocity.magnitude;
        float motor = 0;
        float brakeTorque = 0;
        //float motor = maxMotorTorque * Input.GetAxis("Vertical");
        //float brakeTorque = Mathf.Abs(Input.GetAxis("Jump"));
        //if (brakeTorque > 0) {
        //	brakeTorque = maxMotorTorque;
        //	motor = 0;
        //}
        //else {
        //	brakeTorque = 0;
        //}

        if (UnderAI && TargetSpeed > CurrentSpeed)
        {
            motor = maxMotorTorque;
        }
        else if (UnderAI && TargetSpeed < CurrentSpeed)
        {
            motor = 0;
            brakeTorque = maxMotorTorque;
        }

        pid.error = TargetSteering;
        //Debug.Log(CurrentSteering);
        CurrentSteering = calculatePID();

		foreach (Dot_Truck truck_Info in truck_Infos)
		{
			if (truck_Info.steering == true) {
                //if(Mathf.Abs(CurrentSteering) <= maxSteeringAngle)
                //{
                //    if(Input.GetAxis("Horizontal") > 0) CurrentSteering += SteeringPower;
                //    else if(Input.GetAxis("Horizontal") < 0) CurrentSteering -= SteeringPower;
                //}
                //else
                //{
                //    if(CurrentSteering>0) CurrentSteering = maxSteeringAngle;
                //    else CurrentSteering = -1 * maxSteeringAngle;
                //}
                truck_Info.rightWheel.steerAngle = truck_Info.leftWheel.steerAngle = CurrentSteering;

            }

			if (truck_Info.motor == true)
			{
				truck_Info.leftWheel.motorTorque = motor;
				truck_Info.rightWheel.motorTorque = motor;
			}

			truck_Info.leftWheel.brakeTorque = brakeTorque*100;
			truck_Info.rightWheel.brakeTorque = brakeTorque*100;

			VisualizeWheel(truck_Info);
		}

	}

float calculatePID()
    {
        pid.P = pid.error;
        pid.I = pid.I + pid.error;
        pid.D = pid.error - pid.previousError;
        float PIDvalue = (pid.Kp * pid.P) + (pid.Ki * pid.I) + (pid.Kd * pid.D);
        pid.previousError = pid.error;
        return PIDvalue;
    }

void RenderTextureToPng()
    {
        RenderTexture.active = rt;
        png_tex.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
        png_tex.Apply();
        PngFromCam = png_tex.EncodeToPNG();
    }


}