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
MyT interaction library
"""
import glob
import json
import logging
import os
from pathlib import Path
import sys

import pendulum
import requests

logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s: %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

CACHE_DIR = 'cache'
USER_DATA = 'user_data.json'


class Myt:
    """
    Class for interacting with Toyota vehicle API
    """
    def __init__(self):
        """
        Create cache directory, try to load existing user data or if it doesn't exists do login.
        """
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.config_data = self._get_config()
        self.user_data = self._get_user_data()
        if self.user_data:
            self.headers = {'X-TME-TOKEN': self.user_data['token']}
        else:
            self.login()

    @staticmethod
    def _get_config(config_file='myt.json'):
        """
        Load configuration values from config file. Return config as a dict.
        :param config_file: Filename on configs directory
        :return: dict
        """
        with open(Path('configs')/config_file) as f:
            try:
                config_data = json.load(f)
            except Exception as e:  # pylint: disable=W0703
                log.error('Failed to load configuration JSON! %s', str(e))
                raise
        return config_data

    @staticmethod
    def _get_user_data():
        """
        Try to load existing user data from CACHE_DIR. If it doesn't exists or is malformed return None
        :return: user_data dict or None
        """
        try:
            with open(Path(CACHE_DIR) / USER_DATA) as f:
                try:
                    user_data = json.load(f)
                except Exception as e:  # pylint: disable=W0703
                    log.error('Failed to load cached user data JSON! %s', str(e))
                    raise
            return user_data
        except FileNotFoundError:
            return None

    @staticmethod
    def _read_file(file_path):
        """
        Load file contents or return None if loading fails
        :param file_path: Path for a file
        :return: File contents
        """
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except (FileNotFoundError, TypeError):
            return None

    @staticmethod
    def _write_file(file_path, contents):
        """
        Write string to a file
        :param file_path: Path for a file
        :param contents: String to be written
        :return:
        """
        with open(file_path, 'w') as f:
            f.write(contents)

    @staticmethod
    def _find_latest_file(path):
        """
        Return latest file with given path pattern or None if not found
        :param path: Path expression for directory contents. Like 'cache/trips/trips*'
        :return: Latest file path or None if not found
        """
        files = glob.glob(path)
        if files:
            return max(files, key=os.path.getctime)
        return None

    def login(self, locale='fi-fi'):
        """
        Do Toyota SSO login. Saves user data for configured account in self.user_data and sets token to self.headers.
        User data is saved to CACHE_DIR for reuse.
        :param locale: Locale for login is required but doesn't seem to have any effect
        :return: None
        """
        login_headers = {'X-TME-BRAND': 'TOYOTA', 'X-TME-LC': locale, 'Accept': 'application/json, text/plain, */*',
                         'Sec-Fetch-Dest': 'empty'}
        log.info('Logging in...')
        r = requests.post('https://ssoms.toyota-europe.com/authenticate', headers=login_headers, json=self.config_data)
        if r.status_code != 200:
            raise ValueError('Login failed, check your credentials! {}'.format(r.text))
        user_data = r.json()
        self.user_data = user_data
        self.headers = {'X-TME-TOKEN': user_data['token']}
        self._write_file(Path(CACHE_DIR) / USER_DATA, r.text)

    def get_trips(self, trip=1):
        """
        Get latest 10 trips. Save trips to CACHE_DIR/trips/trips-`datetime` file. Will save every time there is a new
        trip or daily because of changing metadata if no new trips. Saved information is not currently used for
        anything.
        :param trip: There is paging, but it doesn't seem to do anything. 1 is the default value.
        :return: recentTrips dict
        """
        trips_path = Path(CACHE_DIR) / 'trips'
        trips_file = trips_path / 'trips-{}'.format(pendulum.now())
        log.info('Fetching trips...')
        r = requests.get(
            'https://cpb2cs.toyota-europe.com/api/user/{}/cms/trips/v2/history/vin/{}/{}'.format(
                self.user_data['customerProfile']['uuid'], self.config_data['vin'], trip), headers=self.headers)
        if r.status_code != 200:
            raise ValueError('Failed to get data, {} {}'.format(r.status_code, r.headers))
        os.makedirs(trips_path, exist_ok=True)
        previous_trip = self._read_file(self._find_latest_file(str(trips_path / 'trips*')))
        if r.text != previous_trip:
            self._write_file(trips_file, r.text)
        trips = r.json()
        return trips

    def get_trip(self, trip_id):
        """
        Get trip info. Trip is identified by uuidv4. Save trip data to CACHE_DIR/trips/[12]/[34]/uuid file. If given
        trip already exists in CACHE_DIR just get it from there.
        :param trip_id: tripId to fetch. uuid v4 that is received from get_trips().
        :return: trip dict
        """
        trip_base_path = Path(CACHE_DIR) / 'trips'
        trip_path = trip_base_path / trip_id[0:2] / trip_id[2:4]
        trip_file = trip_path / trip_id
        if not trip_file.exists():
            log.debug('Fetching trip...')
            r = requests.get('https://cpb2cs.toyota-europe.com/api/user/{}/cms/trips/v2/{}/events/vin/{}'.format(
                self.user_data['customerProfile']['uuid'], trip_id, self.config_data['vin']), headers=self.headers)
            if r.status_code != 200:
                raise ValueError('Failed to get data {} {}'.format(r.status_code, r.headers))
            os.makedirs(trip_path, exist_ok=True)
            self._write_file(trip_file, r.text)
            trip_data = r.json()
        else:
            with open(trip_file) as f:
                trip_data = json.load(f)
        return trip_data

    def get_parking(self):
        """
        Get location information. Location is saved when vehicle is powered off. Save data to
        CACHE_DIR/parking/parking-`datetime` file. Saved information is not currently used for anything. When vehicle
        is powered on again tripStatus will change to '1'.
        :return: Location dict
        """
        parking_path = Path(CACHE_DIR) / 'parking'
        parking_file = parking_path / 'parking-{}'.format(pendulum.now())
        token = self.user_data['token']
        uuid = self.user_data['customerProfile']['uuid']
        vin = self.config_data['vin']
        headers = {'Cookie': f'iPlanetDirectoryPro={token}', 'VIN': vin}
        url = f'https://myt-agg.toyota-europe.com/cma/api/users/{uuid}/vehicle/location'
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise ValueError('Failed to get data {} {}'.format(r.status_code, r.headers))
        os.makedirs(parking_path, exist_ok=True)
        previous_parking = self._read_file(self._find_latest_file(str(parking_path / 'parking*')))
        if r.text != previous_parking:
            self._write_file(parking_file, r.text)
        return r.json()


def main():
    """
    Get trips, get parking information, get trips information
    :return:
    """
    myt = Myt()

    # Try to fetch trips array with existing user_info. If it fails, do new login and try again.
    try:
        trips = myt.get_trips()
    except ValueError:
        log.info('Failed to use cached token, doing fresh login...')
        myt.login()
        trips = myt.get_trips()

    # Check is vehicle is still parked or moving and print corresponding information. Parking timestamp is epoch
    # timestamp with microseconds. Actual value seems to be at second precision level.
    parking = myt.get_parking()
    if parking['tripStatus'] == '0':
        print('Car is parked at {} at {}'.format(parking['event']['address'],
                                                 pendulum.from_timestamp(int(parking['event']['timestamp']) / 1000).
                                                 in_tz(myt.config_data['timezone']).to_datetime_string()))
    else:
        print('Car left from {} parked at {}'.format(parking['event']['address'],
                                                     pendulum.from_timestamp(int(parking['event']['timestamp']) / 1000).
                                                     in_tz(myt.config_data['timezone']).to_datetime_string()))

    # Get detailed information about trips and calculate cumulative kilometers and fuel liters
    kms = 0
    ls = 0
    for trip in trips['recentTrips']:
        trip_data = myt.get_trip(trip['tripId'])
        stats = trip_data['statistics']
        # Parse UTC datetime strings to local time
        start_time = pendulum.parse(trip['startTimeGmt']).in_tz(myt.config_data['timezone']).to_datetime_string()
        end_time = pendulum.parse(trip['endTimeGmt']).in_tz(myt.config_data['timezone']).to_datetime_string()
        # Remove country part from address strings
        start = trip['startAddress'].split(',')
        end = trip['endAddress'].split(',')
        start_address = '{},{}'.format(start[0], start[1])
        end_address = '{},{}'.format(end[0], end[1])
        kms += stats['totalDistanceInKm']
        ls += stats['fuelConsumptionInL']
        average_consumption = (stats['fuelConsumptionInL']/stats['totalDistanceInKm'])*100
        print('{} {} -> {} {}: {} km, {} km/h, {:.2f} l/100 km'.format(start_time, start_address, end_time,
                                                                       end_address, stats['totalDistanceInKm'],
                                                                       stats['averageSpeedInKmph'],
                                                                       average_consumption))

    print('Total distance: {:.3f} km, Fuel consumption: {:.2f} l, {:.2f} l/100 km'.format(kms, ls, (ls/kms)*100))


if __name__ == "__main__":
    sys.exit(main())
