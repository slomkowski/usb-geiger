import configparser
import os
import time
import unittest

from updaters.radmon_org import RadmonOrgUpdater


class RadmonOrgTest(unittest.TestCase):
    _config_section = "radmon.org"

    def __init__(self, method_name):
        super().__init__(method_name)
        config_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "../../test-configuration.ini"))
        self._config = configparser.ConfigParser()
        with open(config_path) as f:
            self._config.read_file(f)

    def tearDown(self):
        """We sleep between tests, because radmon.org prevents fast subsequent calls."""
        time.sleep(15)

    def test_send_without_position(self):
        config = configparser.ConfigParser()
        config.read_dict({'radmon.org': {
            'enabled': True,
            'user': self._config.get(self._config_section, 'user'),
            'password': self._config.get(self._config_section, 'password'),
        }})
        u = RadmonOrgUpdater(config)
        u.update(time.gmtime(), cpm=15)

    def test_send_with_position(self):
        config = configparser.ConfigParser()
        config.read_dict({'radmon.org': {
            'enabled': True,
            'user': self._config.get(self._config_section, 'user'),
            'password': self._config.get(self._config_section, 'password'),
            'latitude': 52.0,
            'longitude': 17.0
        }})
        u = RadmonOrgUpdater(config)
        u.update(time.gmtime(), cpm=14)


if __name__ == '__main__':
    unittest.main()
