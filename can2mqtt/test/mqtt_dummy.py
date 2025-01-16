class MqttDummy():

  def publish(self, topic, data):
    self.topic = topic
    self.data = data

