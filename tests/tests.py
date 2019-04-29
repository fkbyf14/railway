import functools
import unittest
from railway import railway
from railway.railway import Train, Section, SheduleItem


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                f(*new_args)

        return wrapper

    return decorator


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.railway_config = {'a': {"b": 20, "capacity": 1}, 'b': {"a": 20, "c": 20, "d": 20, "capacity": 1},
                               'c': {"b": 20, "capacity": 1}, 'd': {"b": 20, "e": 20, "g": 20, "capacity": 1},
                               'e': {"d": 20, "h": 20, "f": 20, "k": 20, "capacity": 1},
                               'h': {"e": 20, "g": 20, "capacity": 1},
                               'g': {"d": 20, "h": 20, "capacity": 1}, 'f': {"e": 20, "k": 20, "capacity": 2},
                               'k': {"e": 20, "f": 20, "capacity": 2}}
        self.traffic_service = railway.TrafficService(self.railway_config)
        self.traffic_service.sections_timetable = {'de': Section(section_name='de', length=20,
                                                                 shedule=[SheduleItem(departure=0, arrival=1.0,
                                                                                      train=Train(train_number='256',
                                                                                                  route=['d', 'e', 'f',
                                                                                                         'k'],
                                                                                                  speed=20))]),
                                                   'ef': Section(section_name='ef', length=20,
                                                                 shedule=[SheduleItem(departure=1.0, arrival=2.0,
                                                                                      train=Train(train_number='256',
                                                                                                  route=['d', 'e', 'f',
                                                                                                         'k'],
                                                                                                  speed=20))]),
                                                   'fk': Section(section_name='fk', length=20,
                                                                 shedule=[SheduleItem(departure=2.0, arrival=3.0,
                                                                                      train=Train(train_number='256',
                                                                                                  route=['d', 'e', 'f',
                                                                                                         'k'],
                                                                                                  speed=20))])}

    @cases([
        ["a", "b"],
        ["a", "b", "d", "e", "f"],
        ["k", "f", "e", "h"],
        ['g', 'h', 'g', 'd', 'b']
    ])
    def test_valid_route(self, route):
        self.assertTrue(self.traffic_service.route_validator(route))

    @cases([
        ["a", "c"],
        ["a", "a"],
        ["k", "f", "h", "f"],
        ["g", "b", "d"]
    ])
    def test_invalid_route(self, route):
        self.assertFalse(self.traffic_service.route_validator(route))

    @cases([
        {"train_number": "734", "speed": 20, "route": ["a", "b"]},
        {"train_number": "734", "speed": 40, "route": ["c", "b", "d", "e"]},
        {"train_number": "734", "speed": 18, "route": ["h", "g", "h", "e"]},
        {"train_number": "734", "speed": 15, "route": ["e", "k"]},
        {"train_number": "734", "speed": 10, "route": ["k", "f"]}

    ])
    def test_commit_valid_route(self, train):
        train = Train(train.get('train_number'), train.get('route'), train.get('speed'))
        self.traffic_service.commit_route_into_timetable(train)
        self.assertEqual(len(self.traffic_service.accidents), 0)

    @cases([
        {"train_number": "734", "speed": 20, "route": ["e", "d"]},
        {"train_number": "734", "speed": 20, "route": ["d"]},
        {"train_number": "734", "speed": 40, "route": ["d"]},
        {"train_number": "734", "speed": 20, "route": ["h", "e", "k"]},
        {"train_number": "734", "speed": 10, "route": ["f", "k"]}

    ])
    def test_commit_invalid_route(self, train):
        train = Train(train.get('train_number'), train.get('route'), train.get('speed'))
        self.traffic_service.commit_route_into_timetable(train)
        self.assertEqual(len(self.traffic_service.accidents), 1)


if __name__ == '__main__':
    unittest.main()
