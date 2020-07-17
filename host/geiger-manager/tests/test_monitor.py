import configparser
import time
import unittest
from unittest import TestCase
from unittest.mock import patch

import monitor
import updaters


class DummyUpdater(updaters.BaseUpdater):
    full_name = "updater used in tests only"


class TestMonitor(TestCase):

    @patch('usbcomm.Connector')
    def test_running(self, MockConnector):
        usb = MockConnector()
        usb.get_cpm_and_radiation.return_value = (20.0, 0.15)
        config = configparser.ConfigParser()
        config.read_dict({'monitor': {'interval': 10}})

        m = monitor.Monitor(config, usb)

        self.assertEqual(4, len(m._updaters))

        m.start()

        time.sleep(15)

        m.stop()

        # assert usb is usbcomm.Connector
        # self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
