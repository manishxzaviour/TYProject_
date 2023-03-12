#include <I2Cdev.h>
#include <MPU6050_6Axis_MotionApps20.h>
#include<FastLED.h>
#include <Wire.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <PID_v1.h>
#include <I2Cdev.h>
#include <Wire.h>

String ssid = "LARA";
String pwd = "LARA1234";

IPAddress staticIP(192, 168, 0, 30);
IPAddress subnet(255, 255, 255, 0);
IPAddress gateway(192, 168, 0, 1);
IPAddress primaryDNS(192, 168, 0, 1);

const int step_pin=0;
const int dir_pin=0;
const int zeroB=0;
const int interupt_pin=0;
bool dir=0;
const int led_pin=0;
const int pot_pin=0;
CRGBArray<1> led;
ESP8266WebServer server(80);
MPU6050 mpu;


bool dmpReady = false;  // set true if DMP init was successful
uint8_t mpuIntStatus;   // holds actual interrupt status byte from MPU
uint8_t devStatus;      // return status after each device operation (0 = success, !0 = error)
uint16_t packetSize;    // expected DMP packet size (default is 42 bytes)
uint16_t fifoCount;     // count of all bytes currently in FIFO
uint8_t fifoBuffer[64]; // FIFO storage buffer

Quaternion qq;           // [w, x, y, z]         quaternion container
VectorInt16 aa;         // [x, y, z]            accel sensor measurements
VectorInt16 aaReal;     // [x, y, z]            gravity-free accel sensor measurements
VectorInt16 aaWorld;    // [x, y, z]            world-frame accel sensor measurements
VectorFloat gravity;    // [x, y, z]            gravity vector
float euler[3];         // [psi, theta, phi]    Euler angle container
float ypr[3];           // [yaw, pitch, roll] 

unsigned long currentMillis;
long previousMillis = 0;    
unsigned long count;
unsigned int rodL=0;
unsigned int pos=0;
unsigned int center= rodL/2; 
float rad_to_deg = 180/3.141592654;

float pot1;
float output1;
float actAvg;
int IMUdataReady = 0;
volatile bool mpuInterrupt = false;     // indicates whether MPU interrupt pin has gone high
float pitch;
float roll;

double Pk1 = 0.3; 
double Ik1 = 4;
double Dk1 = 0.005;

double Setpoint1, Input1, Output1;    // PID variables
PID PID1(&Input1, &Output1, &Setpoint1, Pk1, Ik1 , Dk1, DIRECT);

template<class T> inline Print& operator <<(Print &obj,     T arg) {
  obj.print(arg);
  return obj;
}
template<>        inline Print& operator <<(Print &obj, float arg) {
  obj.print(arg, 4);
  return obj;
}

void rFile(char *f, int a)
{
  File file = SPIFFS.open(f, "r");
  if (file)
  {
    String s;
    while (file.available())
    {
      s += char(file.read());
    }
    switch (a)
    {
    case 0:
      server.send(200, "text/html", s);
      break;
    case 1:
      server.send(200, "text/css", s);
      break;
    case 2:
      server.send(200, "text/javascript", s);
      break;
      file.close();
    }
  }
  else
  {
    server.send(404, "text/html", "Error: File does not exist");
  }
}
void Index()
{
  rFile("/index.html", 0);
}
void style()
{
  rFile("/style.css", 1);
}
void IndexJs()
{
  rFile("/index.js", 2);
}
void hNF()
{
  server.send(404, "text/plain", "404 : FnF");
}
void mAnti(){
    digitalWrite(dir_pin,LOW);
    dir=0;
}
void mClk(){
    digitalWrite(dir_pin,HIGH);
    dir=1;
}
void ota()
{
  ArduinoOTA.setHostname("Lara_Balance_controller8266");
  ArduinoOTA.onStart([]()
                     {
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH) {
      type = "sketch";
    } else { // U_FS
      type = "filesystem";
    }
	// SPIFFS.end();
    Serial.println("Start updating " + type); });
    ArduinoOTA.onEnd([]()
                   {
    Serial.println("\nEnd");
	ESP.restart(); });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total)
                        { Serial.printf("Progress: %u%%\r", (progress / (total / 100))); });
  ArduinoOTA.onError([](ota_error_t error)
                     {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) {
      Serial.println("Auth Failed");
    } else if (error == OTA_BEGIN_ERROR) {
      Serial.println("Begin Failed");
    } else if (error == OTA_CONNECT_ERROR) {
      Serial.println("Connect Failed");
    } else if (error == OTA_RECEIVE_ERROR) {
      Serial.println("Receive Failed");
    } else if (error == OTA_END_ERROR) {
      Serial.println("End Failed");
    } });
  ArduinoOTA.begin();
  server.send(200, "text/plain", "ok");
  while(1){
    ArduinoOTA.handle();
  }
}
void setup()
{
    Serial.begin(115200);
    FastLED.addLeds<WS2812, led_pin, GRB>(led,1);
    WiFi.mode(WIFI_STA);
    WiFi.config(staticIP, gateway, subnet, primaryDNS);
    WiFi.begin(ssid.c_str(), pwd.c_str());
    while (WiFi.status() != WL_CONNECTED)
    {
        led[0]=CRGB(255,255,255);
        FastLED.show();
        delay(500);
        led[0]=CRGB(255,255,255);
        FastLED.show();
        delay(500);
        Serial.print(".");
    }
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.print("Camera Ready! Use 'http://");
    Serial.print(WiFi.localIP());
    Serial.println("' to connect");
    pinMode(step_pin,OUTPUT);
    pinMode(dir_pin,OUTPUT);
    pinMode(zeroB,INPUT_PULLUP);
    pinMode(pot_pin,INPUT);
    server.begin();
    server.on("/", Index);
    server.on("/css", style);
    server.on("/ota", ota);
    server.on("/index.js", IndexJs);
    server.onNotFound(hNF);
    mAnti();
    led[0]=CRGB(255,255,0);
    FastLED.show();

    Wire.begin();
    Wire.setClock(400000);
    mpu.initialize();
    devStatus = mpu.dmpInitialize();
    mpu.setXGyroOffset(116);
    mpu.setYGyroOffset(-32);
    mpu.setZGyroOffset(9);
    mpu.setXAccelOffset(-1356);
    mpu.setYAccelOffset(-478);
    mpu.setZAccelOffset(1134);

    if (devStatus == 0) {
    // turn on the DMP, now that it's ready
    mpu.setDMPEnabled(true);

    // enable Arduino interrupt detection
    attachInterrupt(interupt_pin, dmpDataReady, RISING);
    mpuIntStatus = mpu.getIntStatus();

    // get expected DMP packet size for later comparison
    packetSize = mpu.dmpGetFIFOPacketSize();
  } else {
    // ERROR!
    // 1 = initial memory load failed
    // 2 = DMP configuration updates failed
    // (if it's going to break, usually the code will be 1)
    Serial.print(F("DMP Initialization failed (code "));
    Serial.print(devStatus);
    Serial.println(F(")"));
    led[0]=CRGB(255,0,0);
    FastLED.show();
  }
    PID1.SetMode(AUTOMATIC);              
    PID1.SetOutputLimits(-20, 20);
    PID1.SetSampleTime(10);

    while(1){
        if(digitalRead(zeroB)==0){
            break;
        }
        digitalWrite(step_pin,HIGH);
        delayMicroseconds(100);
        digitalWrite(step_pin,LOW);
        delayMicroseconds(100);
    }
    led[0]=CRGB(50,100,0);
    FastLED.show();
    mClk();
    for(pos=0;pos<center;pos++){
        digitalWrite(step_pin,HIGH);
        delayMicroseconds(100);
        digitalWrite(step_pin,LOW);
        delayMicroseconds(100);
    }
    while (1)
    {
        led[0]=CRGB(0,255,0);
        FastLED.show();
        delay(100);
        led[0]=CRGB(0,255,0);
        FastLED.show();
        delay(100);
        // if imu value stable break
    }
}

void loop()
{
    server.handleClient();
    currentMillis = millis();
  if (currentMillis - previousMillis >= 10) {  // start timed event

    previousMillis = currentMillis;

    // check for IMU inpterrupt, read the data if it's ready
    if (IMUdataReady == 1) {
      readAngles();      
    }

    // roll = (ypr[1] * 180 / M_PI);
    pitch = (ypr[2] * 180 / M_PI);

    // get switches and pots
    pot1 = analogRead(A0);
    pot1 = (pot1-512) / 200;

//    actAvg = odrive1.readFloat(); //motor step pos out of 200 and 0 ; 0 after switch pos
    Input1 = pitch;        
    Setpoint1 = pot1;
    PID1.Compute();
    Serial.println(output1);    //output1 to motor
   } 
}
