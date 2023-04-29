import serial.tools.list_ports
import serial
import sys
import time
import requests, json
from Adafruit_IO import MQTTClient


AIO_USERNAME = "LamVinh"
AIO_KEY = "aio_HUyW98JRfR6disI1VkEDqEZ9f7G0"
AIO_FEED_IDS = ["button1", "fan",'humi-info','temp-info','motion', 'light2']
URL = "http://127.0.0.1:8000/api/insertSensorData/"
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
    if feed_id == "fan":
        payload = "f" + payload
    
    if feed_id == 'humi-info':
        send_request(payload, "Humid", "Hu", "Working Room")
    
    if feed_id == 'temp-info':
        send_request(payload, "Temp", "Te", "Working Room")
    
    if feed_id == 'motion':
        send_request(payload, "Motion", "Mo", "Working Room")

    if feed_id == 'light2':
        send_request(payload, "Light", "Li", "Working Room")

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
            # elif splitData[1] == "CHECK":
            #     client.publish("check-pass", splitData[2])
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

def send_request(payload, name, type, room):
    data = {
        "name" : name,
        "type": type,
        "room": room,
        "value": payload
    }
    print(data)
    response = requests.post(url=URL, data=json.dumps(data), headers=HEADERS)
    if response.status_code == 201:
        print("Insert Successful!")
    else:
        print("Something went wrong!")


while True:
    if isMicrobitConnected:
        readSerial()

    time.sleep(1)