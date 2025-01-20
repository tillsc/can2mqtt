import can

class CanListener(can.Listener):
  def __init__(self, dbc_db, mqtt_client, config):
    self.last = {}
    self.first_underscores_to_slash = False
    self.prefix = False
    self.resend_unchanged_events_after = 30
    if 'mqtt' in config:
      if 'topic_names' in config['mqtt']:
        if 'first_underscores_to_slash' in config['mqtt']['topic_names']:
          self.first_underscores_to_slash = config['mqtt']['topic_names']['first_underscores_to_slash']
        if 'prefix' in config['mqtt']['topic_names']:
          self.prefix = config['mqtt']['topic_names']['prefix']
    if 'resend_unchanged_events_after' in config:
      self.resend_unchanged_events_after = config['resend_unchanged_events_after']
    
    self.dbc_db = dbc_db
    self.mqtt_client = mqtt_client

  def on_message_received(self, m):
    msg = None
    try:
      msg = self.dbc_db.decode_message(m.arbitration_id, m.data)
    except KeyError: 
      pass

    if msg != None:
      self.handle_message(msg, m.timestamp)

  def handle_message(self, msg, timestamp):  
    for signal_id in msg:
      topic = signal_id.lower()
      if self.first_underscores_to_slash:
        topic = topic.replace("_", "/", self.first_underscores_to_slash)
      if self.prefix:
        topic = self.prefix + topic
      data = round(msg[signal_id], 5)
      if self.resend_unchanged_events_after == 0 or \
        topic not in self.last or \
        self.last[topic]['data'] != data or \
        timestamp - self.last[topic]['timestamp'] > self.resend_unchanged_events_after:
          self.last[topic] = {'data': data, 'timestamp': timestamp}
          self.mqtt_client.publish(topic, data)
