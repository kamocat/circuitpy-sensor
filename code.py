import board
import busio
import adafruit_bmp280
import digitalio
import os
import time
import ssl, socketpool, wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import json
import versions
import watchdog
import adafruit_logging
import microcontroller
wdt = microcontroller.watchdog
log = adafruit_logging.getLogger("errors")

pin = digitalio.DigitalInOut(board.GP17) #Used here to control the bmp280 I2C address
pin.direction = digitalio.Direction.OUTPUT
pin.value = True
i2c = busio.I2C(board.GP19, board.GP18) #SCL,SDA
sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

status_topic = "home/office/status"
cmd_topic = "home/office/cmd"

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

    client.subscribe( cmd_topic ) # I want to listen to this topic
    discovery_topic = 'home/device/'+versions.uid+'/config'
    discovery_payload = {
  "dev": {
    "mf": "RaspberryPi",
    "mdl": versions.hw,
    "sw": versions.cp,
    "ids": versions.uid,
    "name": "office",
  },
  "o": {
    "name": "RP2350 MQTT Sensor",
    "sw": versions.sw,
  },
  "cmps": {
    versions.uid+'_1': {
      "unique_id": versions.uid+'_1',
      "p": "sensor",
      "name": "pressure",
      "device_class": "atmospheric_pressure",
      "unit_of_measurement": "hPa",
      "value_template": "{{value_json.pressure}}",
    },
    versions.uid+'_2': {
      "unique_id": versions.uid+'_2',
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
    wdt.feed()
    mqtt_client.loop(timeout=1)  # see if any messages to me

    if time.monotonic() - last_msg_send_time > 30.0:  # send a message every 30 secs
        last_msg_send_time = time.monotonic()
        msg = {'temperature': sensor.temperature, 'pressure':sensor.pressure }
        mqtt_client.publish( status_topic, json.dumps(msg) )
        print("sending MQTT msg..", status_topic, msg)
