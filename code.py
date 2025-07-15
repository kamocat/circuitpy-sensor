import board
import time
import busio
import adafruit_bmp280
import digitalio
import os
import ssl, socketpool, wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import watchdog
import adafruit_logging
import microcontroller
from watchdog import WatchDogMode
import adafruit_ntp
import discovery

# Start watchdog
wdt = microcontroller.watchdog
wdt.timeout = 5
# wdt.mode = WatchDogMode.RESET
# Set up logging
log = adafruit_logging.Logger("errors", level=0)
try:
    log.addHandler(
        adafruit_logging.RotatingFileHandler(
            "/errors.log", maxBytes=65536, backupCount=32
        )
    )
    log.addHandler(adafruit_logging.StreamHandler())
    print("Logging to file")
except Exception as e:
    print(f"Not logging to file due to {e}")

# Set up I2C temperature/pressure sensor
pin = digitalio.DigitalInOut(board.GP17)  # Used here to control the bmp280 I2C address
pin.direction = digitalio.Direction.OUTPUT
pin.value = True
i2c = busio.I2C(board.GP19, board.GP18)  # SCL,SDA
sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

# Set up MQTT device discovery
device = discovery.Device("testbench")


def get_temperature():
    return sensor.temperature


def get_pressure():
    return sensor.temperature

'''
device.register_cmp(
    discovery.Sensor(
        "temperature",
        get_temperature,
        device_class="temperature",
        unit_of_measurement="°C",
    )
)
device.register_cmp(
    discovery.Sensor(
        "pressure",
        get_pressure,
        device_class="atmospheric_pressure",
        unit_of_measurement="hPa",
    )
)'''
device.register_cmp(discovery.Number("anumber"))
device.register_cmp(discovery.Text("sometext"))


# Connect to WiFi
print(f"Connecting to {os.getenv('CIRCUITPY_WIFI_SSID')}")
wifi.radio.connect(
    os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD")
)

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
    log.info("Connected to MQTT broker!")

    client.subscribe(device.cmd_topic)  # I want to listen to this topic
    client.publish(device.discovery_topic, device.discovery_payload(), retain=True)


# Called when the client is disconnected
def disconnected(client, userdata, rc):
    log.warning("Disconnected from MQTT broker!")


# Called when a topic the client is subscribed to has a new message
def message(client, topic, message):
    log.info("New message on topic {0}: {1}".format(topic, message))
    if topic == device.cmd_topic:
        device.set(message)


# Set the callback methods defined above
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message

log.info("Connecting to MQTT broker...")
mqtt_client.connect()

# Set up NTP
pool = socketpool.SocketPool(wifi.radio)
ntp = adafruit_ntp.NTP(pool, tz_offset=0, cache_seconds=3600)


def timestamp():
    now = ntp.datetime
    now = [f"{x:02d}" for x in now]
    d = "/".join(now[:3])
    t = ":".join(now[3:6])
    return f"{d} {t}"


log.info(timestamp())

last_msg_send_time = time.monotonic() - 30
while True:
    wdt.feed()
    mqtt_client.loop(timeout=1)  # see if any messages to me

    if time.monotonic() - last_msg_send_time > 5:
        last_msg_send_time = time.monotonic()
        msg = device.get()
        mqtt_client.publish(device.status_topic, msg)
        print("sending MQTT msg..", device.status_topic, msg)
