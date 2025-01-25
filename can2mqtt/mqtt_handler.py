import paho.mqtt.client as mqtt
import time
import json

class MqttHandler():
  def __init__(self, mqtt_config, can_bus, converter):
    self.mqtt_config = mqtt_config
    self.can_bus = can_bus
    self.converter = converter

    self.connect()

  def on_connect(self, client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT broker with result code {reason_code}")
    self.subscribe()

  def on_message(self, client, userdata, message):
    raw_msg = None
    try:
      print("MQTT Message to be sent to can%s: %s" % (message.topic, message.payload))
      raw_msg = self.converter.mqtt2can(message)
    except ValueError: 
      print('Decoding MQTT message has failed')
    
    if raw_msg:
      print(raw_msg)
      self.can_bus.send(raw_msg)

  def connect(self):
    self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
  
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message

    self.client.username_pw_set(username = self.mqtt_config.get('username'), password = self.mqtt_config.get('password'))
    host = self.mqtt_config.get('host', 'localhost')
    print("Trying to connect to MQTT broker at %s..." % host)
    self.client.connect(host)
    
  def subscribe(self):
    if self.converter.send_to_can_from_topic:
      topic = "%s/#" % self.converter.send_to_can_from_topic
      print(topic, "<<<")
      self.client.subscribe(topic)
      print("Listening to '%s' for incoming mqtt messages to send to can bus" % topic)

  def publish(self, topic, data):
    self.client.publish(topic, data)  

  def loop_forever(self):
    self.client.loop_forever()
