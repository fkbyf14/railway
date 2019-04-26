import json
import os
import tempfile
import unittest

import railway


class MainTestCase(unittest.TestCase):
    def setUp(self):
        # Create temporary directory structure
        self._temp_dir = temp_dir = tempfile.mkdtemp()
        #config_path = os.path.join(temp_dir, 'railway_config')
        self.routes_path = os.path.join(temp_dir, 'routes')
        routes_1 = [{"train_number" : "256", "speed": 20, "route": ["b", "d", "e", "f"]},
                    {"train_number" : "734", "speed": 20, "route": ["e", "d"]}]
        # Create config file
        with open(self.routes_path, 'wt') as config:
            for route in routes_1:
                config.write(json.dumps(route))

        self.railway_config = {'a': {"b": 20, "capacity": 1}, 'b': {"a": 20, "c": 20, "d": 20, "capacity": 1},
                          'c': {"b": 20, "capacity": 1}, 'd': {"b": 20, "e": 20, "g": 20, "capacity": 1},
                          'e': {"d": 20, "h": 20, "f": 20, "capacity": 1}, 'h': {"e": 20, "g": 20, "capacity": 1},
                          'g': {"d": 20, "h": 20, "capacity": 1}, 'f': {"e": 20, "capacity": 1}}

    def test_inserted_routes_1(self):
        self.assertEqual((railway.__main__(self.railway_config), self.routes_path)), {'734': 'On the "Station(name=\'d\','
                                                                                         'capacity=1, passing={'
                                                                                         '\'time\': \'256\', '
                                                                                         '1.0: {\'256\', \'734\'}})" '
                                                                                         'station is bad accident: '
                                                                                         'too many trains: {\'256\', '
                                                                                         '\'734\'}'}





if __name__ == '__main__':
    unittest.main()