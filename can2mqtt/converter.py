import json
import can
import re

class Converter():
  def __init__(self, dbc_db, config):
    self.dbc_db = dbc_db
    self.only_one_signal_per_message = config.get('only_one_signal_per_message', False)
    self.send_to_can_from_topic = config.get('send_to_can_from_topic')

    name_conversion_config = config.get('name_conversion', {})
    self.first_underscores_to_slash = name_conversion_config.get('first_underscores_to_slash', False)
    self.prefix = name_conversion_config.get('prefix')

  def can2mqtt(self, raw_can_msg):
    signal_data = None
    try:
      signal_data = self.dbc_db.decode_message(raw_can_msg.arbitration_id, raw_can_msg.data)
    except KeyError:
      return None, None

    dbc_msg = self.dbc_db.get_message_by_frame_id(raw_can_msg.arbitration_id)
    topic = self.message_name_to_topic(dbc_msg.name)
    data = None
    if self.only_one_signal_per_message:
      data = round(signal_data[dbc_msg.signals[0].name], 5)
    else:
      data = {}
      for signal_id in signal_data:
        data[signal_id] = round(signal_data[signal_id], 5)
      data = json.dumps(data)
    return topic, data  

  def mqtt2can(self, mqtt_message):
    if not self.send_to_can_from_topic:
      return
      
    sub_topic = re.sub("^%s/" % self.send_to_can_from_topic, "", mqtt_message.topic)
    message_name = self.topic_to_message_name(sub_topic)
    if not message_name:
      return

    dbc_msg = self.dbc_db.get_message_by_name(message_name)
    
    signal_data = json.loads(mqtt_message.payload)
    if self.only_one_signal_per_message:
      signal_data = { dbc_msg.signals[0].name: signal_data }

      

    return can.Message(arbitration_id=dbc_msg.frame_id, data = dbc_msg.encode(signal_data))

  def message_name_to_topic(self, message_name):
    topic = message_name.lower()
    if self.first_underscores_to_slash:
      topic = topic.replace("_", "/", self.first_underscores_to_slash)
    if self.prefix:
      topic = self.prefix + topic
    return topic

  def topic_to_message_name(self, topic):
    message_name = topic.upper()
    if self.first_underscores_to_slash:
      message_name = message_name.replace("/", "_", self.first_underscores_to_slash)
    if self.prefix:
      message_name = re.sub("^#{self.prefix}", "", message_name)
    return message_name