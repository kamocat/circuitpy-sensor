import versions
import adafruit_logging
log = adafruit_logging.getLogger('errors')

'''MQTT Device
Should only have one of these, as it uses the microcontroller's UID
https://www.home-assistant.io/integrations/mqtt/#device-discovery-payload
'''
class Device:
    def __init__(self, name, prefix='home'):
        self.name = name
        self.cmps = []
        self.status_topic = '/'.join([prefix, name, 'status'])
        self.cmd_topic =    '/'.join([prefix, name, 'cmd'])
        self.discovery_topic = '/'.join([prefix, 'device', versions.uid, 'cmd'])
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
  "state_topic": self.status_topic,
  "command_topic": self.cmd_topic,
}
    def register_cmp(self, cmp):
        uid = f'{versions.uid}_{len(self.cmps)}'
        cmp.attributes['unique_id'] = uid
        self.cmps.append(cmp)
        self.payload['cmps'][uid] = cmp.attributes
    def unregister_cmp(self, cmp):
        if cmp in self.cmps:
            self.cmps.remove(cmp)
            uid = cmp.attributes['unique_id']
            self.payload['cmps'][uid] = {'name':cmp.attributes['name']}
        else:
            log.error(f"Can't remove component {cmp.attributes['name']}")
    def get(self):
        return {c.name: c.get() for c in self.cmps if hasattr(c,'get')}
    def set(self,val):
        for c in self.cmps:
            if c.name in val and hasattr(c, 'set'):
                c.set(val[c.name])

'''MQTT Sensor 
https://www.home-assistant.io/integrations/sensor.mqtt/
'''
class Sensor:
    def __init__(self,name,getter,**kwargs):
        self.name = name
        self.get = getter
        self.attributes = {'name':name, 'value_template':f'{{value_json.name}}'}
        self.attributes.update(kwargs)

