import os
import tempfile
import unittest

import railway


class MainTestCase(unittest.TestCase):

    def setUp(self):
        # Create temporary directory structure
        self._temp_dir = temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, 'railway_config')
        routes_path = os.path.join(temp_dir, 'routes')

        # Create config file
        with open(config_path, 'wt') as config:
            config.write(dict(a={"b": 20}, b={"a": 20, "c": 20, "d": 20}, c={"b": 20}, d={"b": 20, "e": 20, "g": 20},
                              e={"d": 20, "h": 20, "f": 20}, h={"e": 20, "g": 20}, g={"d": 20, "h": 20}, f={"e": 20}))


