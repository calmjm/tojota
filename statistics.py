# Copyright 2020 Janne Määttä
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Get, parse and print driving statistics from MyT API
"""
import argparse
import sys

import pendulum

from tojota import Myt


def parse_args():
    """
    Parse command line arguments
    :return: arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', required=False, dest='from_date', help='Get statistics beginning from date YYYY-MM-DD')
    parser.add_argument('-i', required=False, dest='interval', default='day',
                        help='Statistics granularity, day/week/year')
    args = parser.parse_args()
    return args


def parse_daily_driving_statistics(myt, data):
    """
    Parse daily statistics
    :param myt: MyT object
    :param data: statistics data
    :return:
    """
    for item in data['histogram']:
        year = item['bucket']['year']
        # pendulum formatter expects date to have three characters to be accepted as day of the year. Add leading zeros.
        day_of_year = f"{item['bucket']['dayOfYear']:03d}"
        date = pendulum.from_format(f'{year} {day_of_year}', 'YYYY DDDD', tz=myt.config_data['timezone'])
        data = item['data']
        print('{}: EV: {:.1f}/{:.1f} km, {:.0f}%, avg speed: {:.0f} km/h, max speed: {:.0f} km/h'.
              format(date.format('YYYY-MM-DD'), data['evDistanceInKm'],
                     data['totalDistanceInKm'], data['evDistancePercentage'],
                     data['averageSpeedInKmph'], data['maxSpeedInKmph']))


def parse_weekly_driving_statistics(data):
    """
    Parse weekly statistics
    :param data: statistics data
    :return:
    """
    for item in data['histogram']:
        year = item['bucket']['year']
        week = item['bucket']['week']
        date = '{} W{}'.format(year, week)
        data = item['data']
        print('{}: EV: {:.1f}/{:.1f} km, {:.0f}%, avg speed: {:.0f} km/h, max speed: {:.0f} km/h'.
              format(date.format('YYYY-MM-DD'), data['evDistanceInKm'],
                     data['totalDistanceInKm'], data['evDistancePercentage'],
                     data['averageSpeedInKmph'], data['maxSpeedInKmph']))


def parse_yearly_driving_statistics(data):
    """
    Parse yearly statistics
    :param data: statistics data
    :return:
    """
    data = data['summary']
    print('EV: {:.1f}/{:.1f} km, {:.0f}%, avg speed: {:.0f} km/h, max speed: {:.0f} km/h'.
          format(data['evDistanceInKm'],
                 data['totalDistanceInKm'], data['evDistancePercentage'],
                 data['averageSpeedInKmph'], data['maxSpeedInKmph']))


def main():
    """
    Get, parse and print driving statistics from MyT API
    :return:
    """
    args = parse_args()
    myt = Myt()
    interval = None
    from_date = None
    if args.interval == 'day':
        interval = args.interval
        from_date = pendulum.now().subtract(days=30).format('YYYY-MM-DD')
    if args.interval == 'week':
        interval = args.interval
        from_date = pendulum.now().subtract(days=120).format('YYYY-MM-DD')
    if args.interval == 'year':
        interval = None
        from_date = pendulum.now().subtract(days=365).format('YYYY-MM-DD')
    if args.from_date:
        from_date = args.from_date

    data, fresh = myt.get_driving_statistics(from_date, interval)
    if args.interval == 'day':
        parse_daily_driving_statistics(myt, data)
    if args.interval == 'week':
        parse_weekly_driving_statistics(data)
    if args.interval == 'year':
        parse_yearly_driving_statistics(data)


if __name__ == "__main__":
    sys.exit(main())
