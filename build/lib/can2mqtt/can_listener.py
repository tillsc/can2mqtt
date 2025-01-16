import can

class CanListener(can.Listener):

    first_ts = 0
    last = {}
    first_underscores_to_slash = False
    prefix = False

    def __init__(self, db, mqtt_client, config):
      if 'mqtt' in config:
        if 'topic_names' in config['mqtt']:
          if 'first_underscores_to_slash' in config['mqtt']['topic_names']:
            self.first_underscores_to_slash = config['mqtt']['topic_names']['first_underscores_to_slash']
          if 'prefix' in config['mqtt']['topic_names']:
            self.prefix = config['mqtt']['topic_names']['prefix']
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
            xxx
            topic = topic.replace('_', '/', self.first_underscores_to_slash)
          if self.prefix:
            topic = self.prefix + topic
          data = round(msg[signal_id], 5)
          if topic not in self.last or self.last[topic]['data'] != data or m.timestamp - self.last[topic]['timestamp'] > 60:
            self.last[topic] = {'data': data, 'timestamp': m.timestamp}
            self.mqtt_client.publish(topic, data)
      except KeyError:
        pass
