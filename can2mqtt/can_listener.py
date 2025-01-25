import can

class CanListener(can.Listener):
  def __init__(self, mqtt_handler, converter, resend_unchanged_events_after):
    self.last = {}
    self.mqtt_handler = mqtt_handler
    self.converter = converter
    self.resend_unchanged_events_after = resend_unchanged_events_after

  def on_message_received(self, m):
    topic, data = self.converter.can2mqtt(m)
    
    if topic:
      if self.resend_unchanged_events_after == 0 or \
        topic not in self.last or \
        self.last[topic]['data'] != data or \
        m.timestamp - self.last[topic]['timestamp'] > self.resend_unchanged_events_after:
          self.last[topic] = {'data': data, 'timestamp': m.timestamp}
          self.mqtt_handler.publish(topic, data)
