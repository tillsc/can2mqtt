class MqttDummy():

  last_topic = None
  last_data = None

  def publish(self, topic, data):
    self.last_topic = topic
    self.last_data = data

  def reset(self):
    self.last_topic = None
    self.last_data = None
