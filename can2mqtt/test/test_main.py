import unittest 
  
import can
import struct
import time

from can2mqtt.test.mqtt_dummy import MqttDummy
from can2mqtt.can_listener import CanListener
from can2mqtt.converter import Converter
from can2mqtt.app import load_dbc_db

class TestStringMethods(unittest.TestCase): 
  
  def setUp(self):
    self.mqtt_dummy = MqttDummy()
    self.dbc_db = load_dbc_db(['can2mqtt/test/simple.dbc'])
    self.default_config = { 
      'name_conversion': { 
        'first_underscores_to_slash': 2 
      },
      'only_one_signal_per_message': True
    }
    self.converter = Converter(self.dbc_db, self.default_config)

  def build_can_listener(self, resend_unchanged_events_after):
    return CanListener(self.mqtt_dummy, self.converter, resend_unchanged_events_after)
  

  def build_message(self, message_id, data_byte_1 = 0, timestamp=None):
    if timestamp == None:
      timestamp = time.time()
    return can.Message(timestamp=timestamp, arbitration_id=500, \
      data=struct.pack('4b', data_byte_1, 0, 0, 0))

  def test_can_listener_converts_topic_names(self):
    can_listener = self.build_can_listener(30)
    msg = self.build_message(500, 50)
    can_listener.on_message_received(msg)
    self.assertEqual(self.mqtt_dummy.last_topic, 'io/debug/msg1')
    self.assertEqual(self.mqtt_dummy.last_data, 50)

  def test_no_resend_same_data(self):
    can_listener = self.build_can_listener(30)
    
    msg = self.build_message(500, 50)
    can_listener.on_message_received(msg)
    self.assertEqual(self.mqtt_dummy.last_topic, 'io/debug/msg1')
    self.assertEqual(self.mqtt_dummy.last_data, 50)
    
    self.mqtt_dummy.reset()
    can_listener.on_message_received(msg)
    self.assertEqual(self.mqtt_dummy.last_topic, None)

    self.mqtt_dummy.reset()
    msg2 = self.build_message(500, 50, msg.timestamp + 20)
    can_listener.on_message_received(msg2)
    self.assertEqual(self.mqtt_dummy.last_topic, None)

    self.mqtt_dummy.reset()
    msg3 = self.build_message(500, 50, msg.timestamp + 31)
    can_listener.on_message_received(msg3)
    self.assertEqual(self.mqtt_dummy.last_topic, 'io/debug/msg1')

  def test_force_resend_same_data(self):
    can_listener = self.build_can_listener(0)
    
    msg = self.build_message(500, 50)
    for x in range(0, 3):
      can_listener.on_message_received(msg)
      self.assertEqual(self.mqtt_dummy.last_topic, 'io/debug/msg1')
      self.assertEqual(self.mqtt_dummy.last_data, 50)
      self.mqtt_dummy.reset()

if __name__ == "__main__":
    unittest.main() 