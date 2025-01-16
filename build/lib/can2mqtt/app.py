import can
import cantools
import paho.mqtt.client as mqtt
import yaml
import threading
from can2mqtt.can_listener import CanListener

def load_config():
  with open('config.yaml', 'r') as stream:
    return yaml.load(stream)

def load_dbc_db(dbc_files):
  db = cantools.database.Database()
  for file in dbc_files:
    with open (file, 'r') as fin:
      db.add_dbc(fin)
  return db

def main_program(config, dbc_db):
    mqtt_client = mqtt.Client('can2mqtt')
    mqtt_client.username_pw_set(username=config['mqtt']['username'],password=config['mqtt']['password'])
    mqtt_client.connect(config['mqtt']['host'])

    can_listener = CanListener(dbc_db, mqtt_client)
    bus = can.interface.Bus(bustype='socketcan', channel=config['can']['interface'], bitrate=config['can']['bitrate'])
    can.Notifier(bus, [can_listener])

    threading.Event().wait()
