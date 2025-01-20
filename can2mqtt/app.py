import can
import cantools
import paho.mqtt.client as mqtt
import yaml
import threading
from can2mqtt.can_listener import CanListener

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
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.username_pw_set(username=config['mqtt']['username'],password=config['mqtt']['password'])
    mqtt_client.connect(config['mqtt']['host'])

    can_listener = CanListener(dbc_db, mqtt_client, config)
    bus = can.interface.Bus(bustype='socketcan', channel=config['can']['interface'], bitrate=config['can']['bitrate'])
    can.Notifier(bus, [can_listener])

    threading.Event().wait()
