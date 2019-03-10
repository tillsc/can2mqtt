#!/usr/bin/python3

import can
import cantools
import paho.mqtt.client as mqtt
import yaml

try:
  with open("config.yaml", 'r') as stream:
    config = yaml.load(stream)
except FileNotFoundError as exc:
  print("Could not open file 'config.yaml'")
  exit(1)
except yaml.YAMLError as exc:
  print("Could not parse file 'config.yaml':")
  print(exc)
  exit(1)

class CanListener(can.Listener):

    first_ts = 0
    last = {}
    first_underscores_to_slash = False
    prefix = False
    if 'topic_names' in config['mqtt']:
      if 'first_underscores_to_slash' in config['mqtt']['topic_names']:
        first_underscores_to_slash = config['mqtt']['topic_names']['first_underscores_to_slash']
      if 'prefix' in config['mqtt']['topic_names']:
        prefix = config['mqtt']['topic_names']['prefix']

    def __init__(self, db, mqtt_client):
      self.db = db
      self.mqtt_client = mqtt_client

    def on_message_received(self, m):
      if self.first_ts == 0:
          self.first_ts = m.timestamp

      try:
        msg = self.db.decode_message(m.arbitration_id, m.data)
        for signal_id in msg:
          topic = signal_id.lower()
          if self.first_underscores_to_slash:
            topic = topic.replace("_", "/", self.first_underscores_to_slash)
          if self.prefix:
            topic = self.prefix + topic
          data = round(msg[signal_id], 5)
          if topic not in self.last or self.last[topic]['data'] != data or m.timestamp - self.last[topic]['timestamp'] > 60:
            self.last[topic] = {'data': data, 'timestamp': m.timestamp}
            self.mqtt_client.publish(topic, data)
      except KeyError:
        pass



def main_program():
    mqtt_client = mqtt.Client('can2mqtt')
    mqtt_client.username_pw_set(username=config['mqtt']['username'],password=config['mqtt']['password'])
    mqtt_client.connect('hassio.fritz.box')
    bus = can.interface.Bus(bustype='socketcan', channel=config['can']['interface'], bitrate=config['can']['bitrate'])

    db = cantools.database.Database()
    for file in config['dbc_files']:
      with open (file, 'r') as fin:
        db.add_dbc(fin)

    can_listener = CanListener(db, mqtt_client)
    can.Notifier(bus, [can_listener])

    while True:
      pass

main_program()
