import unittest 
  
import can
import struct

from can2mqtt.test.mqtt_dummy import MqttDummy
from can2mqtt.can_listener import CanListener
from can2mqtt.app import load_dbc_db

class TestStringMethods(unittest.TestCase): 
  
  def test_can_listener_converts_topic_names(self):
    mqtt_dummy = MqttDummy()

    config = {}
    can_listener = CanListener(load_dbc_db(['can2mqtt/test/simple.dbc']), mqtt_dummy, config)

    message = can.Message(arbitration_id=500, data=struct.pack('4b', 0, 0, 0, 50))
    can_listener.on_message_received(message)
    self.assertEqual(mqtt_dummy.topic, 'io_debug_test_unsigned')


if __name__ == "__main__":
    unittest.main() 