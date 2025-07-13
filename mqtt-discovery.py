import versions
import adafruit_logging
log = adafruit_logging.getLogger('errors')

'''MQTT Device
Should only have one of these, as it uses the microcontroller's UID
https://www.home-assistant.io/integrations/mqtt/#device-discovery-payload
'''
class Device:
    def __init__(self, name, prefix='/home'):
        self.name = name
        self.period = update_period
        self.status_topic = '/',join([prefix, name, 'status'])
        self.cmd_topic =    '/',join([prefix, name, 'cmd'])
        self.discovery_topic =    '/',join([prefix, 'device', versions.uuid, 'cmd'])
        self.payload = {
  "dev": {
    "mf": "RaspberryPi",
    "mdl": versions.hw,
    "sw": versions.cp,
    "ids": versions.uid,
    "name": name,
  },
  "o": {
    "name": "RP2350 MQTT Sensor",
    "sw": versions.sw,
  },
  "cmps": {
  },
  "qos": 2,
  "state_topic": status_topic,
  "command_topic": cmd_topic,
}
    self.cmps = []
    def register_cmp(cmp):
        uid = versions.uid + '_' + len(cmps)
        cmp.a['unique_id'] = uid
        self.cmps.append(cmp)
        self.payload['cmps'][uid] = cmp.attributes
    def unregister_cmp(cmp):
        if cmp in self.cmps:
            self.cmps.remove(cmp)
            uid = cmp.attributes['unique_id']
            self.payload['cmps'][uid] = {'name':cmp.attributes['name']}
        else:
            log.error(f"Can't remove component {cmp.attributes['name']}")
    def get():
        return {c.name: c.get() for c in cmps if hasattr(c,'get')}
    def set(val):
        for c in cmps:
            if c.name in val and hasattr(c, 'set'):
                c.set(val[c.name])

'''MQTT Sensor 
https://www.home-assistant.io/integrations/sensor.mqtt/
'''
class Sensor:
    def __init__(self,name,attributes={}):
        self.name = name
        self.attributes = {'name':name, 'p':'sensor', 'value_template':f'{{value_json.{name} }}'}
        self.attributes.update{attributes}
    def get():
        #Define your own function and overwite this
        return None 

