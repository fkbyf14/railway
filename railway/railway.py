import argparse
import json
import logging
import sys
from collections import namedtuple

DEFAULT_CONFIG_PATH = 'railway_config.conf'
DEFAULT_ROUTE_CONFIG_PATH = 'routes.conf'

Train = namedtuple('Train', ['train_number', 'route', 'velocity'])
Section = namedtuple('Section', ['section_name', 'length', 'shedule'])
SheduleItem = namedtuple('SheduleItem', ['departure', 'arrival', 'train'])
Station = namedtuple('Station', ['name', 'capacity', 'passing'])


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
        self.sections_timetable = dict()
        self.stations_timing = dict()
        self.accidents = {}

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
        if self.sections_timetable.get(section_name):
            self.sections_timetable.get(section_name).shedule.append(shedule_item)
        else:
            section = Section(section_name, distance, [shedule_item])
            self.sections_timetable[section_name] = section

    def analyze_section_shedule(self, section_name):
        shedule = self.sections_timetable.get(section_name).shedule
        last_shedule_item = shedule[-1]
        for i in range(0, len(shedule) - 1):
            if not (shedule[i].departure >= last_shedule_item.arrival or
                    shedule[i].arrival <= last_shedule_item.departure):
                if shedule[i].train != last_shedule_item.train:
                    raise TrainAccidentError(r'On the "{0}" section is bad accident: '
                                             'intersection of {1} and {2}'.format(section_name, shedule[i],
                                                                                  last_shedule_item))

    def analyze_station_passing(self, station_name, time, train_number):
        if self.stations_timing.get(station_name):
            station = self.stations_timing.get(station_name)
            if not station.passing.get(time):
                station.passing[time] = {train_number}
            else:
                station.passing.get(time).add(train_number)
                try:
                    if station.capacity < len(station.passing.get(time)):
                        raise TrainAccidentError(r'On the "{0}" station is bad accident: '
                                                 'too many trains in the moment {1}'.format(station, time))
                except TypeError:
                    logging.error(r'Please enter the capacity for "{}" station'.format(station))
        else:
            station = Station(station_name, self.railway_conf.get(station_name).get('capacity'), {time: {train_number}})
            self.stations_timing[station_name] = station

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
            self.analyze_station_passing(left_bound, departure, train_number)
            self.analyze_section_shedule(section_name)
            self.analyze_station_passing(right_bound, arrival, train_number)


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
                if not traffic_service.accidents:
                    logging.info("It is the first accident:")
                traffic_service.accidents.update({train_number: e.message})
                logging.error('Route № {0} has a problem: {1}'.format(train_number, e.message))

    logging.debug("accidents:{}".format(traffic_service.accidents))
    logging.debug("stations_timing:{}".format(traffic_service.stations_timing))
    logging.debug("sections_timetable:{}".format(traffic_service.sections_timetable))
    return traffic_service.accidents


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
