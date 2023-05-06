import serial.tools.list_ports
import serial
import sys
import time
import requests, json
from Adafruit_IO import MQTTClient
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


AIO_USERNAME = "LamVinh"
AIO_KEY = "aio_Ikez49d4P246pxMzFVEajaKqqH7S"
AIO_FEED_IDS = ['button1', 'fan', 'check', 'password','humi-info','temp-info','motion', 'light2']
# URL = "http://127.0.0.1:8000/api/insertSensorData/"
URL = "http://192.168.137.38:8000/api/"
# URL = "http://127.0.0.1:8000/api/"
URL_SENSOR = URL + "insertSensorData/"
URL_DEVICE = URL + "controlDeviceFromGateway/"
URL_SERVO = URL + "controlServo/"
HEADERS = {"Content-Type":"application/json"}
# =======
# AIO_USERNAME = "your user name"
# AIO_KEY = "your key"
# AIO_FEED_IDS = ["your-feed-light", "your-feed-fan"]
# >>>>>>> 4cae6cfd35f2ccf30629abb53b4b6a30b52847c8


def connected(client):
    print("Ket noi thanh cong...")
    for feed in AIO_FEED_IDS:
        client.subscribe(feed)


def subscribe(client, userdata, mid, granted_qos):
    print("Subcribe thanh cong...")


def disconnected(client):
    print("Ngat ket noi...")
    sys.exit(1)


def message(client, feed_id, payload):
    # print("Receiver data from " + client + "/" + feed_id + " : " + payload)
    print("Receiver data from " + feed_id + " : " + payload)
    
    if feed_id == 'humi-info':
        # send_request(URL_SENSOR, 'post', payload, "Humid", "Hu", "Working Room")
        send_request(URL_SENSOR, 'sensor', {"name":"Humid", "type": "Hu", "room":"Working Room", "value":payload})
    
    if feed_id == 'temp-info':
        # send_request(URL_SENSOR, 'post', payload, "Temp", "Te", "Working Room")
        send_request(URL_SENSOR, 'sensor', {"name":"Temp", "type": "Te", "room":"Working Room", "value":payload})

    if feed_id == 'motion':
        # send_request(URL_SENSOR, 'post', payload, "Motion", "Mo", "Working Room")
        send_request(URL_SENSOR, 'sensor', {"name":"Motion", "type": "Mo", "room":"Working Room", "value":payload})

    if feed_id == 'light2':
        # send_request(URL_SENSOR, 'post', payload, "Light", "Li", "Working Room")
        send_request(URL_SENSOR, 'sensor', {"name":"Light", "type": "Li", "room":"Working Room", "value":payload})

    if feed_id == 'button1':
        send_request(URL_DEVICE, 'device', {"name":"Den","value":payload})

    if feed_id == 'fan':
        send_request(URL_DEVICE, 'device', {"name":"Quat","value":payload})
        payload = "f" + payload
    
    if feed_id == 'password':
        send_request(URL_DEVICE, 'device', {"name":"Servo","value":payload})
        payload = "p" + payload
    
    if feed_id == 'check':
        send_request(URL_SERVO, 'device', {"name":"Servo","value":payload})

    if isMicrobitConnected:
        ser.write((str(payload) + "#").encode())


client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()


def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if "USB-SERIAL CH340" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    print(commPort)
    return commPort


isMicrobitConnected = False
if getPort() != "None":
    ser = serial.Serial(port=getPort(), baudrate=115200)
    isMicrobitConnected = True


def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    try:
        if splitData[0] == "1":             # node 1
            if splitData[1] == "TEMP":
                client.publish("temp-info", splitData[2])
            elif splitData[1] == "HUMI":
                client.publish("humi-info", splitData[2])
            elif splitData[1] == "LIGHT":
                client.publish("light2", splitData[2])
            elif splitData[1] == "PASS":
                client.publish("password", splitData[2])
            elif splitData[1] == "MOTION":
                client.publish("motion", splitData[2])
            elif splitData[1] == "CHECK":
                client.publish("check-pass", splitData[2])
        # if splitData[0] == "2":           # node 2
        #     if splitData[1] == "TEMP":
        #         client.publish("bbc-temp1", splitData[2])
        #     elif splitData[1] == "HUMI":
        #         client.publish("bbc-humi1", splitData[2])
    except:
        pass


mess = ""


def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end + 1:]

# def send_request(url, payload, name, type, room):
#     data = {
#         "name" : name,
#         "type": type,
#         "room": room,
#         "value": payload
#     }
#     print(data)
#     response = requests.post(url=url, data=json.dumps(data), headers=HEADERS)
#     if response.status_code == 201:
#         print("Insert Successful!")
#     else:
#         print("Something went wrong!")

def send_request(url, control, request):
    if control == "device":
        response = requests.put(url=url, data=json.dumps(request), headers=HEADERS)
    else:
        response = requests.post(url=url, data=json.dumps(request), headers=HEADERS)

    if response.status_code == 201 or response.status_code == 200:
        print("Insert Successful!")
    else:
        print("Something went wrong!")


while True:
    if isMicrobitConnected:
        readSerial()

    time.sleep(1)