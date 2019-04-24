import argparse
import json
import logging
import sys
from collections import namedtuple

DEFAULT_CONFIG_PATH = 'railway_config'
DEFAULT_ROUTE_CONFIG_PATH = 'routes'

Train = namedtuple('Train', ['train_number', 'route', 'velocity'])
Section = namedtuple('Section', ['section_name', 'length', 'shedule'])
SheduleItem = namedtuple('SheduleItem', ['departure', 'arrival', 'train'])


class TrainAccidentError(Exception):
    def __init__(self, message):
        self.message = message


def load_railway_conf(conf_path):
    with open(conf_path, 'r') as conf_file:
        conf = json.load(conf_file, encoding='UTF-8')
    return conf


def get_route(route_conf_path):
    """load config of routes"""
    with open(route_conf_path, 'r', encoding='UTF-8') as route_file:
        for line in route_file:
            yield json.loads(line)


class TrafficService:
    def __init__(self, railway_conf):
        self.railway_conf = railway_conf
        self.overall_timetable = dict()

    def route_validator(self, route):
        for station in range(len(route) - 1):
            try:
                way = self.railway_conf.get(route[station]).get(route[station + 1])
                if not way:
                    logging.info('Route of train is not valid: there is no way from',
                                 {0}, "to", {1}.format(route[station], route[station + 1]))
                    return
            except AttributeError:
                logging.error(r'There is no adjacent stations to "{}" station in railway config'.format(route[station]))
                return
        return True

    @staticmethod
    def get_section_name(left_bound, right_bound):
        if left_bound < right_bound:
            section_name = '{0}{1}'.format(left_bound, right_bound)
        else:
            section_name = '{0}{1}'.format(right_bound, left_bound)
        return section_name

    def create_or_update_section_into_timetable(self, section_name, shedule_item, distance):
        if self.overall_timetable.get(section_name):
            self.overall_timetable.get(section_name).shedule.append(shedule_item)
        else:
            section = Section(section_name, distance, [shedule_item])
            self.overall_timetable[section_name] = section

    def analyze_section_shedule(self, section_name):
        logging.debug('Overall timetable is {}'.format(self.overall_timetable))
        shedule = self.overall_timetable.get(section_name).shedule
        last_shedule_item = shedule[-1]
        for i in range(0, len(shedule) - 1):
            if not (shedule[i].departure > last_shedule_item.arrival or
                    shedule[i].arrival < last_shedule_item.departure):
                if shedule[i].train != last_shedule_item.train:
                    raise TrainAccidentError(r'On the "{0}" section is bad accident: '
                                             'intersection of {1} and {2}'.format(section_name, shedule[i],
                                                                                  last_shedule_item))

    def commit_route_into_timetable(self, train_number, route, speed):
        for section_number in range(len(route) - 1):
            left_bound = route[section_number]
            right_bound = route[section_number + 1]
            distance = self.railway_conf.get(left_bound).get(right_bound)
            section_name = self.get_section_name(left_bound, right_bound)

            if section_number == 0:
                arrival = 0
            departure = arrival
            arrival = departure + distance / speed
            shedule_item = SheduleItem(departure, arrival, train_number)

            self.create_or_update_section_into_timetable(section_name, shedule_item, distance)
            self.analyze_section_shedule(section_name)


def main(railway_config, routes_path):
    traffic_service = TrafficService(railway_config)
    logging.basicConfig(format='[%(asctime)s] %(levelname).1s %(message)s', level=logging.DEBUG)
    for train in get_route(routes_path):
        train_number = train.get('train_number')
        speed = train.get('speed')
        route = train.get('route')
        if traffic_service.route_validator(route):
            try:
                traffic_service.commit_route_into_timetable(train_number, route, speed)
            except TrainAccidentError as e:
                logging.error('Route № {0} has a problem: {1}'.format(train_number, e.message))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='path to railway config file', default=DEFAULT_CONFIG_PATH)
    parser.add_argument('--routes', help='path to config file of routes', default=DEFAULT_ROUTE_CONFIG_PATH)
    args = parser.parse_args()
    config_path, routes_path = args.config, args.routes
    railway_config = load_railway_conf(config_path)

    try:
        main(railway_config, routes_path)
    except Exception as e:
        logging.exception(sys.exc_info()[0])
