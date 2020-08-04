from unittest import TestCase

from src.main.python import utils


class UtilsTest(TestCase):
    def test_find_updaters(self):
        utils.find_updaters()
