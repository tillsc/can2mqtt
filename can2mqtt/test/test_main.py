import unittest 
  
import can
import struct
import time

from can2mqtt.test.mqtt_dummy import MqttDummy
from can2mqtt.can_listener import CanListener
from can2mqtt.app import load_dbc_db

class TestStringMethods(unittest.TestCase): 
  
  def setUp(self):
    self.mqtt_dummy = MqttDummy()
    self.dbc_db = load_dbc_db(['can2mqtt/test/simple.dbc'])
    self.default_config = { 
      'mqtt': {
         'topic_names': { 
          'first_underscores_to_slash': 2 
          } 
        }
      }

  def build_can_listener(self, special_config = {}):
    cnf = self.default_config | special_config
    return CanListener(self.dbc_db, self.mqtt_dummy, cnf)
  

  def build_message(self, message_id, data_byte_1 = 0):
    return can.Message(timestamp=time.time(), \
      arbitration_id=500, \
      data=struct.pack('4b', data_byte_1, 0, 0, 0)\
    )

  def test_can_listener_converts_topic_names(self):
    can_listener = self.build_can_listener()
    msg = self.build_message(500, 50)
    can_listener.on_message_received(msg)
    self.assertEqual(self.mqtt_dummy.last_topic, 'io/debug/test_unsigned')
    self.assertEqual(self.mqtt_dummy.last_data, 50)

  def test_no_resend_same_data(self):
    can_listener = self.build_can_listener()
    
    msg = self.build_message(500, 50)
    can_listener.on_message_received(msg)
    self.assertEqual(self.mqtt_dummy.last_topic, 'io/debug/test_unsigned')
    self.assertEqual(self.mqtt_dummy.last_data, 50)
    
    self.mqtt_dummy.reset()
    can_listener.on_message_received(msg)
    self.assertEqual(self.mqtt_dummy.last_topic, None)

  def test_force_resend_same_data(self):
    can_listener = self.build_can_listener({'resend_unchanged_events_after': 0})
    
    msg = self.build_message(500, 50)
    for x in range(0, 3):
      can_listener.on_message_received(msg)
      self.assertEqual(self.mqtt_dummy.last_topic, 'io/debug/test_unsigned')
      self.assertEqual(self.mqtt_dummy.last_data, 50)
      self.mqtt_dummy.reset()

if __name__ == "__main__":
    unittest.main() 