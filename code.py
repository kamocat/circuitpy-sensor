import board
import busio
import adafruit_bmp280
import digitalio
import os
import time
import ssl, socketpool, wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import json

pin = digitalio.DigitalInOut(board.GP17) #Used here to control the bmp280 I2C address
pin.direction = digitalio.Direction.OUTPUT
pin.value = True
i2c = busio.I2C(board.GP19, board.GP18)
sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

my_mqtt_topic_hello = "me/feeds/hello"  # the topic we send on
my_mqtt_topic_light = "me/feeds/light"  # the topic we receive on (could be the same)
status_topic = "home/bedroom/status"
cmd_topic = "home/bedroom/cmd"

# Connect to WiFi
print(f"Connecting to {os.getenv('CIRCUITPY_WIFI_SSID')}")
wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=os.getenv("mqtt_broker"),
    port=os.getenv("mqtt_port"),
    username=os.getenv("mqtt_username"),
    password=os.getenv("mqtt_password"),
    socket_pool=socketpool.SocketPool(wifi.radio),
    ssl_context=ssl.create_default_context(),
)

# Called when the client is connected successfully to the broker
def connected(client, userdata, flags, rc):
    print("Connected to MQTT broker!")

    client.subscribe( my_mqtt_topic_light) # say I want to listen to this topic
    discovery_topic = 'home/device/test/config'
    discovery_payload = {
  "dev": {
    "mf": "RaspberryPi",
    "mdl": "pico 2 W",
    "sw": "10.0.0_beta",
    "ids": "test",
    "name": "bedroom",
  },
  "o": {
    "name": "RP2350 MQTT Sensor",
    "sw": "0.0.1",
  },
  "cmps": {
    "bedroom_pressure": {
      "unique_id": "bedroom_pressure",
      "p": "sensor",
      "name": "pressure",
      "device_class": "atmospheric_pressure",
      "unit_of_measurement": "hPa",
      "value_template": "{{value_json.pressure}}",
    },
    "bedroom_temperature": {
      "unique_id": "bedroom_temperature",
      "p": "sensor",
      "name": "temperature",
      "device_class": "temperature",
      "unit_of_measurement": "°C",
      "value_template": "{{value_json.temperature}}",
    }
  },
  "qos": 2,
  "state_topic": status_topic,
  "command_topic": cmd_topic,
}
    client.publish(discovery_topic, json.dumps(discovery_payload), retain=True)

# Called when the client is disconnected
def disconnected(client, userdata, rc):
    print("Disconnected from MQTT broker!")

# Called when a topic the client is subscribed to has a new message
def message(client, topic, message):
    print("New message on topic {0}: {1}".format(topic, message))
    val = 0
    try:
        val = int(message)  # attempt to parse it as a number
    except ValueError:
        pass
    print("setting LED to color:",val)
    # led.fill(val)  # if we had leds

# Set the callback methods defined above
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message

print("Connecting to MQTT broker...")
mqtt_client.connect()

last_msg_send_time = 0

while True:
    mqtt_client.loop(timeout=1)  # see if any messages to me

    if time.monotonic() - last_msg_send_time > 30.0:  # send a message every 30 secs
        last_msg_send_time = time.monotonic()
        msg = {'temperature': sensor.temperature, 'pressure':sensor.pressure }
        mqtt_client.publish( status_topic, json.dumps(msg) )
        print("sending MQTT msg..", status_topic, msg)
