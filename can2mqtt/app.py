import can
import cantools
import yaml
import threading
from can2mqtt.converter import Converter
from can2mqtt.can_listener import CanListener
from can2mqtt.mqtt_handler import MqttHandler

def load_config():
  with open('config.yaml', 'r') as stream:
    return yaml.safe_load(stream)

def load_dbc_db(dbc_files):
  dbc_db = cantools.database.Database()
  for file in dbc_files:
    with open (file, 'r') as fin:
      dbc_db.add_dbc(fin)
  return dbc_db

def main_program(config, dbc_db):
  converter = Converter(dbc_db, config)
  
  can_config = config.get('can', {})
  can_bus = can.interface.Bus(bustype = can_config.get('bustype', 'socketcan'), \
    channel = can_config.get('interface', 'can0'), \
    bitrate = can_config.get('bitrate', 125000))

  mqtt_handler = MqttHandler(config.get('mqtt', {}), can_bus, converter)

  can_listener = CanListener(mqtt_handler, converter, config.get('resend_unchanged_events_after', 30))
  can.Notifier(can_bus, [can_listener])
 
  mqtt_handler.loop_forever()
