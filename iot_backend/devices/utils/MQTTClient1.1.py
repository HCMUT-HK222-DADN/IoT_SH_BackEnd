# Example of using the MQTT client class to subscribe to a feed and print out
# any changes made to the feed.  Edit the variables below to configure the key,
# username, and feed to subscribe to for changes.

# Import standard python modules.
import sys, json, requests

# Import Adafruit IO MQTT client.
from Adafruit_IO import MQTTClient

url = "http://192.168.1.11:8000/api/"
# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
with open('./MQTTConfig.json') as f:
    config = json.load(f)
    # ADAFRUIT_IO_KEY = config['ADAFRUIT_IO_KEY']
    # ADAFRUIT_IO_USERNAME = config['ADAFRUIT_IO_USERNAME']
    ADAFRUIT_IO_USERNAME = "LamVinh"
    ADAFRUIT_IO_KEY = "aio_HUyW98JRfR6disI1VkEDqEZ9f7G0"
    # FEED_ID = config['FEED_ID']["led"]
    # FEED_ID = ['button1','button2','humi-info','temp-info']
    FEED_ID = 'temp-info'
    FEED_ID = ''
    f.close()

# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
# ADAFRUIT_IO_USERNAME = os.environ.get("ADAFRUIT_IO_USERNAME")

# Set to the ID of the feed to subscribe to for updates.
# FEED_ID = os.environ.get("FEED_ID")


# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(FEED_ID))
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe(FEED_ID)

def subscribe(client, userdata, mid, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print('Subscribed to {0} with QoS {1}'.format(FEED_ID, granted_qos[0]))

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    url_insert = url + 'insertSensorData/'
    data = {
        "name": "Light",
        "type": "Li",
        "room": "Working Room",
        "value": payload
    }
    headers = {"Content-Type":"application/json"}
    jsondata = json.dumps(data)
    print(jsondata)
    response = requests.post(url=url_insert, data=jsondata, headers=headers)
    if response.status_code == 201:
        print("OK")
    else: print("Something went wrong!")

    print('Feed {0} received new value: {1}'.format(feed_id, payload))
    


# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message
client.on_subscribe  = subscribe

# Connect to the Adafruit IO server.
client.connect()
client.loop_background()
while True:
    pass
# Start a message loop that blocks forever waiting for MQTT messages to be
# received.  Note there are other options for running the event loop like doing
# so in a background thread--see the mqtt_client.py example to learn more.
# client.loop_blocking()